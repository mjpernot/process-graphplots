#!/usr/bin/python
# Classification (U)

"""Program:  process_graphplots.py

    Description:  Processes imagery graph plot files.  This process entails
        checking the filename to see it is valid and in the correct format
        (i.e. date and time, BE Number, etc).  The file is than checked to see
        if it has been added to the target deck and has a valid BE number
        assigned to it.  Once the graph plot file has passed the validation
        process, the file is then processed for the imagery process, if
        requested.  Afterwards the graphplot file is moved to the archive web
        storage page directory.  A JSON document is produced on all files that
        have been processed and the JSON document is inserted into a Mongodb
        database for web page applications to use and create web pages from.

    Usage:
        process_graphplots.py -c config_file -d config

    Arguments:
        -c file => Graphplots configuration file.  Required arg.
            File will be file_name.py, but without the py extension.
        -d dir path => Directory path to config file (-c). Required arg.

        configuration module -> name is runtime dependent as it can be
            used for different configurations on different servers.

    Notes:
        Configuration file format (file_name.py):
        # Cocoms Process Control
        #   Cocoms in the list run against the specified code section.
        # Commands to have graphplot files validated.
        validate_cmds = ["command_dir", "command_dir", ...]
        # Commands to have the files processed for imagery & web pages.
        process_cmds = ["command_dir", "command_dir", ...]

        # Directory paths
        # Location for the error log.
        error_dir = "/Directory Path"
        # Temporary directory for processing temp files for program.
        temp_dir = "/Directory Path"
        # Directory path to the Region country list files.
        list_dir = "/Directory Path"
        # Base directory containing the command structure for web pages.
        graphbase_dir = "/Directory Path"
        # Directory containing the raw input files.
        gp_dir = "/Directory Path"
        # Base directory for post-processed files.
        archive_dir = "/Directory Path"
        # Directory for JSON files.
        json_dir = "/Directory Path"

        # Directory names (not full directory paths)
        # Directory folder containing the BE number files.
        be_folder = "Directory Name"
        # Directory folder containing the rejected files.
        rejected_folder = "Directory Name"
        # Directory folder containing the .xml file for graphplot files.
        gp_meta_folder = "Directory Name"
        # Directory folder containing files have not been web processed.
        web_nonproc_folder = "Directory Name"

        # File names
        # File name of the Target Deck.
        tgtdeck_file = "Target Deck File"
        # File name for mailed files not found in the Target Deck.
        mail_notdeck_file = "Mail Not In Deck File"
        # File name for rejected graph plot file names.
        gp_reject_file = "Graph Plot Reject File"
        # Name of lock file.
        lock_file = "process_graphplots.lock"

        # Documentum processing directories.
        #   Leave Null if Documentum processing is not required.
        # Directory path where XML file is save to.
        metacard_dir = "/Directory Path"
        # Directory path where graph plot file is save to.
        image_dir = "/Directory Path"

        # Email addresses
        emailfrom = "Email@From_Address"
        # Email address(es) for invalid/reject GP messages.
        emailtowarn = "Email@To_Address, ..."
        # Email address(es) for target not in deck messages.
        emailtotgt = "Email@To_Address, ..."

        # User and Group IDs
        # Imagery User ID
        img_id = Imagery User ID
        # Imagery Group ID
        img_grp = Imagery Group ID
        # Web User ID
        web_id = Web User ID
        # Web Group ID
        web_grp = Web Group ID

        # File and Directory Perms (set in octal)
        # File Perm
        f_perm = 0NNN
        # Directory Perm
        d_perm = 0NNN

    Example:
        process_graphplots.py -c graphplots -d config

"""

# Libraries and Global Variables

# Standard
import sys
import datetime
import os
import re

# Third party
import json

# Local
import lib.arg_parser as arg_parser
import lib.gen_libs as gen_libs
import system
import lib.gen_class as gen_class
import version

# Version
__version__ = version.__version__


def help_message():

    """Function:  help_message

    Description:  Displays the program's docstring which is the help and usage
        message when -h option is selected.

    Arguments:

    """

    print(__doc__)


def setup_validation(GRAPH, dir_set, file_set, **kwargs):

    """Function:  setup_validation

    Description:  Validates the directories and files used by the program.
        Checks for existence and permission settings.  Will create directories
        if the "create" option is set to "True".

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) dir_set -> Dictionary list directories and perms.
        (input) file_set -> Dictionary list of files and perms.
        (input) **kwargs:
            null_dir -> List of directory variables that can be null.
        (output) v_flag -> True|False - Valiation status.

    """

    v_flag = True
    null_dir = kwargs.get("null_dir")

    for dname in dir_set:

        # If directory is listed in null_dir then allow it to be nullable.
        if dname not in null_dir or \
           (dname in null_dir and getattr(GRAPH, dname)):

            status, msg = gen_libs.chk_crt_dir(getattr(GRAPH, dname),
                                               dir_set[dname]["create"],
                                               dir_set[dname]["write"],
                                               dir_set[dname]["read"],
                                               **kwargs)

            if not status:
                v_flag = status
                print(msg)

    for fname in file_set:

        status, msg = gen_libs.chk_crt_file(getattr(GRAPH, fname),
                                            file_set[fname]["create"],
                                            file_set[fname]["write"],
                                            file_set[fname]["read"], **kwargs)

        if not status:
            v_flag = status
            print(msg)

    for cmdname in GRAPH.validate_cmds:

         status, msg = gen_libs.chk_crt_dir(os.path.join(GRAPH.gp_dir,
                                                         cmdname),
                                            False, True, True, **kwargs)

         if not status:
             v_flag = status
             print(msg)

    return v_flag


def fetch_files(GRAPH, **kwargs):

    """Function:  fetch_files

    Description:  Get list of all files from the input directory for each
        command.  Filter the all file list based on extension name(s).
        The all and filtered file lists will be saved to a
        dictionary-list for each command.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            ext_list -> List of extension(s) that are allowed.

    """

    ext_list = kwargs.get("ext_list")

    for cmd in GRAPH.validate_cmds:
        cmd_dir = os.path.join(GRAPH.gp_dir, cmd)

        all_file_list = [x for x in os.listdir(cmd_dir)
                         if os.path.isfile(os.path.join(cmd_dir, x))]

        # Filter the files based the file extension.
        file_list = [x for x in all_file_list
                     if x.endswith(tuple(ext_list))]

        GRAPH.all_file_dict[cmd] = all_file_list
        GRAPH.file_dict[cmd] = file_list


def files_to_proc(list_name, **kwargs):

    """Function:  files_to_proc

    Description:  Check to see if there are files to process in the list for
        each command.  Will return "True" as soon as the first one is found.

    Arguments:
        (input) list_name -> Graph class list name to be checked.
        (input) **kwargs:
            None
        (output) True|False -> Are there files to process.

    """

    for cmd in list_name:

        if list_name[cmd]:
            return True

    return False


def filter_file_names(GRAPH, **kwargs):

    """Function:  filter_file_names

    Description:  Does a regular expression search on each file in the
        dictionary-list.  If the pattern matches then add the file to a
        list and add this list to the filtered file dictionary list for
        each command.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            pattern -> regex search parameter for file names.

    """

    pattern = kwargs.get("pattern")

    for cmd in GRAPH.file_dict:

        # Do a regular expression search on each file and add file to list.
        file_list = [x for x in GRAPH.file_dict[cmd] if re.search(pattern, x)]

        GRAPH.filtered_file_dict[cmd] = file_list


def email_no_tgt_name(GRAPH, F_INST, cmd, **kwargs):

    """Function:  email_no_tgt_name

    Description:  Checks the Class target name to see if set to not in target
        to mean it is not in the Target Deck list.  If the case, then
        check to see if an email notification has been sent on the file.
        If not previously notified, will add to the not in target deck
        list and write to the error log.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) F_INST -> File Graph class instance.
        (input) cmd -> Name of command.
        (input) **kwargs:
            None

    """

    # If Target is not in the Target Deck list.
    if F_INST.tgt_name == "NOT_IN_TARGET_DECK":

        # Has mail notification has not been previously sent.
        if not gen_libs.file_search(GRAPH.mail_notdeck, F_INST.f_be):

            # Add file to "not in target" list and write to log.
            GRAPH.gp_not_in_deck[cmd].append(F_INST.fname)
            gen_libs.write_file2(GRAPH.error_log_hdlr, F_INST.fname +
                                 " is not in target deck and will be mailed.")

        else:
            # Write to log, as has been previously notified of file via email.
            gen_libs.write_file2(GRAPH.error_log_hdlr, F_INST.fname +
                                 " isn't in target deck & has been mailed.")


def dctm_processing(GRAPH, F_INST, **kwargs):

    """Function:  dctm_processing

    Description:  Checks to see if the Documentum processing has been
        requested.  If so, copies the graph plot file and any associated XML
        file to a number of directories and then moves the XML file to the
        Metacard directory.  A number of entries are made to the Class
        stating the file name and location of the files.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) F_INST -> File Graph class instance.
        (input) **kwargs:
            None

    """

    src_dir = os.path.join(GRAPH.gp_dir, F_INST.cmd)

    # If Documentum processing has been requested.
    if GRAPH.image_dir:
        gen_libs.cp_file2(F_INST.fname, src_dir, GRAPH.image_dir,
                          F_INST.new_fname, **kwargs)

        os.chmod(os.path.join(GRAPH.image_dir, F_INST.new_fname), GRAPH.f_perm)
        os.chown(os.path.join(GRAPH.image_dir, F_INST.new_fname), GRAPH.img_id,
                 GRAPH.img_grp)

        F_INST.add_file_loc(F_INST.new_fname, GRAPH.image_dir)

    # If Documentum processing has been requested and an XML file is present.
    if os.path.isfile(os.path.join(src_dir, F_INST.xml_fname)) \
       and GRAPH.metacard_dir:

        F_INST.set_xml()

        gen_libs.cp_file2(F_INST.xml_fname, src_dir, GRAPH.metacard_dir,
                          F_INST.new_xml_fname, **kwargs)

        os.chmod(os.path.join(GRAPH.metacard_dir, F_INST.new_xml_fname),
                 GRAPH.f_perm)
        os.chown(os.path.join(GRAPH.metacard_dir, F_INST.new_xml_fname),
                 GRAPH.img_id, GRAPH.img_grp)

        F_INST.add_file_loc(F_INST.new_xml_fname, GRAPH.metacard_dir)

        gen_libs.mv_file(F_INST.xml_fname, src_dir, GRAPH.gp_meta_dir,
                         F_INST.new_xml_dctm_fname, **kwargs)

        F_INST.add_file_loc(F_INST.new_xml_dctm_fname, GRAPH.gp_meta_dir)


def process_graph_file(GRAPH, F_INST, cmd, **kwargs):

    """Function:  process_graph_file

    Description:  Executes a number of functions to process file graph
        instance.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) F_INST -> File Graph class instance.
        (input) cmd -> Name of command.
        (input) **kwargs:
            None

    """

    # See if a NOT IN DECK TARGET notification has been sent.
    email_no_tgt_name(GRAPH, F_INST, cmd, **kwargs)

    dctm_processing(GRAPH, F_INST, **kwargs)

    gen_libs.rename_file(F_INST.fname, F_INST.new_fname,
                         os.path.join(GRAPH.gp_dir, F_INST.cmd), **kwargs)

    F_INST.upd_to_loc(F_INST.fname, os.path.join(GRAPH.gp_dir, F_INST.cmd),
                      new_fname=F_INST.new_fname)

    GRAPH.gp_valid_list[cmd].append(F_INST.new_fname)


def process_reject(GRAPH, fname, cmd, err_str, **kwargs):

    """Function:  process_reject

    Description:  Processes a reject file by adding to reject dictionary-list,
        writes an error log entry, and moves the file to the reject
        directory.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fname -> File name.
        (input) cmd -> Name of command.
        (input) err_str -> Error string.
        (input) **kwargs:
            None

    """

    GRAPH.reject_dict[cmd].append({fname: err_str})

    gen_libs.write_file2(GRAPH.error_log_hdlr,
                         "File: " + fname + " " + err_str)

    gen_libs.mv_file(fname, os.path.join(GRAPH.gp_dir, cmd),
                     GRAPH.rejected_dir, fname, **kwargs)


def process_dir_files(GRAPH, **kwargs):

    """Function:  process_dir_files

    Description:  Controls the processing of the files in the input directory.
        For each command, takes the filtered file list and rejects any
        file that is empty, has an invalid year, or invalid date and/or
        time.  Creates a F_Graph class instance for each valid file and
        appends the instance to array of class instances and also calls
        functions to process this file.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            None
        (output) fgraph_ary -> Dictionary-list of F_Graph instances.

    """

    fgraph_ary = {}

    for cmd in GRAPH.filtered_file_dict:

        file_loc_list = []
        GRAPH.gp_not_in_deck[cmd] = []
        GRAPH.gp_valid_list[cmd] = []
        GRAPH.reject_dict[cmd] = []

        for fname in GRAPH.filtered_file_dict[cmd]:

            fullname = os.path.join(os.path.join(GRAPH.gp_dir, cmd), fname)

            if os.stat(fullname).st_size == 0:

                err_str = "Rejected:  Zero file size"
                process_reject(GRAPH, fname, cmd, err_str)

                # Check for associated XML file.
                if os.path.isfile(".".join([fullname, "xml"])):

                    gen_libs.write_file2(GRAPH.error_log_hdlr, "File: " +
                                         fname +
                                         ".xml rejected due to 0 file size.")
                    gen_libs.mv_file(".".join([fname, "xml"]),
                                     os.path.join(GRAPH.gp_dir, cmd),
                                     GRAPH.rejected_dir,
                                     ".".join([fname, "xml"]))

                # Go to next file.
                continue

            F_INST = system.FGraph(fname, cmd, GRAPH.tgtdeck, GRAPH.gp_dir)

            # Validate the year range from 1965 to current year.
            #   Year 1965 was selected as it was first imagery file created.
            if not 1965 <= F_INST.f_year \
               <= datetime.datetime.strftime(datetime.datetime.now(), "%Y"):

                err_str = "Rejected: Invalid year"
                process_reject(GRAPH, fname, cmd, err_str)

                # Go to next file and do not add F_INST to file location list.
                continue

            # Validate the date and time.
            elif not gen_libs.validate_date(F_INST.f_date + F_INST.f_time[0:4],
                                            dtg_format="%Y%m%d%H%M"):

                err_str = "Rejected: Invalid datetime"
                process_reject(GRAPH, fname, cmd, err_str)

                # Go to next file and do not add F_INST to file location list.
                continue

            # Save F_Graph class to an array list.
            else:
                file_loc_list.append(F_INST)

            process_graph_file(GRAPH, F_INST, cmd, **kwargs)

        if file_loc_list:
            fgraph_ary[cmd] = file_loc_list

    return fgraph_ary


def fetch_rejected_gps(GRAPH, fgraph_ary, **kwargs):

    """Function:  fetch_rejected_gps

    Description:  Compares the original first filtered list with the current
        F_Graph instance array.  Any files left are rejected.  See if
        a previously notification has been sent out on the rejected
        file and if not add the file to the reject list.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) **kwargs:
            None

    """

    f_hdlr = open(GRAPH.rejected_gps, "r")

    for cmd in GRAPH.file_dict:

        for fname in GRAPH.file_dict[cmd]:

            # Is the file name NOT in the array of F_Graph instances array.
            if not any(F_INST.fname == fname for F_INST in fgraph_ary[cmd]):

                # See if a previously notification has NOT been sent out.
                if not re.search(fname, f_hdlr.read()):

                    # Add the file to the reject list.
                    GRAPH.gp_rejects.append("/".join([cmd, fname]))

                # Reset file pointer for next search.
                f_hdlr.seek(0)

    f_hdlr.close()


def process_rejected_gps(GRAPH, **kwargs):

    """Function:  process_rejected_gps

    Description:  If there are rejected files, processes them by creating an
        email of the rejected files and also adds the rejected files
        to the rejected mailed file for future reference.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            None

    """

    # Are there rejected files.
    if GRAPH.gp_rejects:
        f_hdlr = open(GRAPH.rejected_gps, "a")

        MAIL = gen_class.Mail(GRAPH.emailtowarn,
                              "Invalid Graphplot File Names",
                              GRAPH.emailfrom)
        MAIL.add_2_msg("Invalid file names that were rejected:\n")

        for x in GRAPH.gp_rejects:

            MAIL.add_2_msg(x + "\n")
            gen_libs.write_file2(f_hdlr, x)

        MAIL.send_mail()


def process_notindeck(GRAPH, **kwargs):

    """Function:  process_notindeck

    Description:  Email out a list of files that were not found in the target
        deck list and also adds the file to the not in deck mailed file.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            None

    """

    f_hdlr = open(GRAPH.mail_notdeck, "a")

    MAIL = gen_class.Mail(GRAPH.emailtotgt,
                          "GraphPlots File Name Not In Deck\n",
                          GRAPH.emailfrom)
    MAIL.add_2_msg("File names that are not in the target deck.\n")
    MAIL.add_2_msg("There is no facility name for below mentioned files.\n")
    MAIL.add_2_msg("Target be added to Target Deck along with Be Number.\n")

    for cmd in GRAPH.gp_not_in_deck:

        for x in GRAPH.gp_not_in_deck[cmd]:

            MAIL.add_2_msg("/".join([cmd, x]) + "\n")
            gen_libs.write_file2(f_hdlr, "/".join([cmd, x]))

    MAIL.send_mail()

    f_hdlr.close()


def find_rejects(GRAPH, fgraph_ary, **kwargs):

    """Function:  find_rejects

    Description:  Controls the processing of the rejected files and files not
        found in the target deck.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) **kwargs:
            None

    """

    fetch_rejected_gps(GRAPH, fgraph_ary, **kwargs)

    process_rejected_gps(GRAPH, **kwargs)

    for cmd in GRAPH.gp_not_in_deck:

        if GRAPH.gp_not_in_deck[cmd]:
            process_notindeck(GRAPH, **kwargs)

            # Break as the process_notindeck processes all files.
            break


def create_dir(d_name, owner=-1, group=-1, perm=None, **kwargs):

    """Function:  create_dir

    Description:  Creates a directory with optional arguments for owner and
        group settings along with permission settings.

    Arguments:
        (input) d_name -> Directory name.
        (input) owner -> Numeric id for owner.  -1 leaves id unchanged.
        (input) group -> Numeri id for group.  -1 leaves id unchanged.
        (input) perm -> Octal permission setting.
        (input) **kwargs:
            None

    """

    if not os.path.isdir(d_name):
        os.makedirs(d_name)
        os.chown(d_name, owner, group)

        if perm:
            os.chmod(d_name, perm)


def process_fgraph_dir(GRAPH, fgraph_ary, cc, reg_dir, be_list, **kwargs):

    """Function:  process_fgraph_dir

    Description:  Moves the graph plot file to the correct web directory
        location.  Creates the necessary directories if they do not exist.
        Updates F_Graph instance to the new location and sets the processed
        attribute within the class.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) cc -> Country name.
        (input) reg_dir -> Region path directory.
        (input) be_list -> List of BE Numbers.
        (input) **kwargs:
            None

    """

    for cmd in fgraph_ary:

        for f_inst in fgraph_ary[cmd]:

            # Check to see if file's BE number is in the BE list.
            if f_inst.f_be in be_list:
                f_inst.set_dirs(cc, reg_dir)

                create_dir(f_inst.cc_dir, GRAPH.web_id, GRAPH.web_grp,
                           GRAPH.d_perm, **kwargs)
                create_dir(f_inst.gp_dir, GRAPH.web_id, GRAPH.web_grp,
                           GRAPH.d_perm, **kwargs)
                create_dir(f_inst.yy_dir, GRAPH.web_id, GRAPH.web_grp,
                           GRAPH.d_perm, **kwargs)
                create_dir(f_inst.mm_dir, GRAPH.web_id, GRAPH.web_grp,
                           GRAPH.d_perm, **kwargs)

                gen_libs.mv_file(f_inst.new_fname,
                                 os.path.join(GRAPH.gp_dir, cmd),
                                 f_inst.mm_dir)

                f_inst.upd_to_loc(f_inst.new_fname,
                                  os.path.join(GRAPH.gp_dir, cmd),
                                  new_path=f_inst.mm_dir)

                f_inst.set_processed()


def process_fgraph_web(GRAPH, fgraph_ary, **kwargs):

    """Function:  process_fgraph_web

    Description:  Pulls the F_Graph attributes and converts them to a
        dictionary format.  All of the instances are saved to a dictionary
        which is then converted to a JSON document and written to a file.
        Process File Graph instances for web entry.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) **kwargs:
            None

    """

    jdoc = {}

    for cmd in fgraph_ary:

        for f_inst in fgraph_ary[cmd]:

            if f_inst.processed is True:
                # Pull class information and save to dictionary.
                jdoc[f_inst.new_fname] = f_inst.__dict__

    # Convert dictionary to JSON and write to file.
    gen_libs.write_file(GRAPH.json_doc, "w", json.dumps(jdoc, indent=4))


def process_region_cc(GRAPH, fgraph_ary, f_cc, reg_dir, tgt_dir, **kwargs):

    """Function:  process_region_cc

    Description:  Process each country in the Region Country list by creating a
        list of BE numbers for the region and passing this to the
        function to process the graph plot files.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) f_cc -> Region Country List file name.
        (input) reg_dir -> Region path directory.
        (input) tgt_dir -> Region Target path directory.
        (input) **kwargs:
            None

    """

    with open(f_cc) as fname:
        for cc in fname:

            # Clean up the country name.
            cc = cc.strip()

            # Create the BE number file name.
            #   "_benums" is the default ending for the BE file name.
            f_be = os.path.join(GRAPH.benum_dir, "".join([cc, "_benums"]))

            # If the BE file does not exist, file is empty or not readable.
            if not os.path.isfile(f_be) or os.stat(f_be).st_size == 0 \
               or not os.access(f_be, os.R_OK):

                gen_libs.write_file2(GRAPH.error_log_hdlr,
                                     "Error: No file, empty, non-readable: " +
                                     f_be)

                # Go to the next country.
                continue

            else:
                with open(f_be) as fname2:
                    # Read BEs into a list, clean up the BE number.
                    be_list = [x.strip() for x in fname2]

            # Process the F_Graph instances.
            process_fgraph_dir(GRAPH, fgraph_ary, cc, reg_dir, be_list)


def process_valid_files(GRAPH, fgraph_ary, **kwargs):

    """Function:  process_valid_files

    Description:  Setup the Region's country list file and directories and then
        call the function to process each country in the region.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) fgraph_ary -> Dictionary-list of F_Graph instances.
        (input) **kwargs:
            None

    """

    for region in GRAPH.process_cmds:

        # Create the Region's Country list file name.
        #   "-country_list" is default ending for the Country list file name.
        f_cc = os.path.join(GRAPH.list_dir, "".join([region, "-country_list"]))

        # If the Region Country list file does not exist, file is empty
        #   or not readable.
        if not os.path.isfile(f_cc) or os.stat(f_cc).st_size == 0 \
           or not os.access(f_cc, os.R_OK):

            gen_libs.write_file2(GRAPH.error_log_hdlr,
                                 "Error: No file, empty, or non-readable: " +
                                 f_cc)

            # Go to the next command.
            continue

        # NOTE: "targets" directory may not be required if the web pages are
        #   created from the Mongodb database.
        # Create the Region's directory variables.
        reg_dir = os.path.join(GRAPH.graphbase_dir, region)
        tgt_dir = os.path.join(reg_dir, "targets")

        create_dir(reg_dir, GRAPH.web_id, GRAPH.web_grp, GRAPH.d_perm,
                   **kwargs)
        create_dir(tgt_dir, GRAPH.web_id, GRAPH.web_grp, GRAPH.d_perm,
                   **kwargs)

        # Process each Country within the Region.
        process_region_cc(GRAPH, fgraph_ary, f_cc, reg_dir, tgt_dir, **kwargs)


def find_nonproc_files(GRAPH, **kwargs):

    """Function:  find_nonproc_files

    Description:  Compare the current list of files in the input directories
        with the original file list.  Any files listed means the file was
        not processed.  Send out an email on non-processed files and
        write entry to error log.  Also looks for files that have
        passed name validation, but have failed for another reason and
        handles those files by moving them to another directory and
        sending out email and log notifications.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            fgraph_ary ->  Dictionary-list of F_Graph instances.

    """

    full_list = {}
    proc_flag = False

    for cmd in GRAPH.validate_cmds:

        cmd_dir = os.path.join(GRAPH.gp_dir, cmd)

        # Return all files in the commands's input directory as a list.
        all_file_list = [x for x in os.listdir(cmd_dir)
                         if os.path.isfile(os.path.join(cmd_dir, x))]

        # Intersect the original file list with the current file list.
        diff_list = list(set(GRAPH.all_file_dict[cmd]) & set(all_file_list))

        # Any file listed means it was not processed.
        if diff_list:
            # Add the list to a dictionary-list.
            full_list[cmd] = diff_list
            proc_flag = True

    # If any files were detected that were not processed.
    if proc_flag:
        MAIL = gen_class.Mail(GRAPH.emailtowarn, "Non-Processed File Names",
                              GRAPH.emailfrom)
        MAIL.add_2_msg("File names that were not processed:\n")

        for cmd in full_list:

            for fname in full_list[cmd]:
                MAIL.add_2_msg(fname + "\n")
                gen_libs.write_file2(GRAPH.error_log_hdlr, cmd + "/" + fname +
                                     ":  File was not processed.")

        MAIL.send_mail()

    # 20160830 - Added handling of valid name non-processed files.
    ###########################################################################
    fgraph_ary = kwargs.get("fgraph_ary", None)
    file_list = []

    # Have any files been processed.
    if fgraph_ary:

        for cmd in fgraph_ary:

            for f_inst in fgraph_ary[cmd]:

                # If file has not been processed.
                if f_inst.processed is False:

                    file_list.append("/".join([f_inst.cmd, f_inst.new_fname]))

                    # Move file to non-processed directory.
                    gen_libs.mv_file(f_inst.new_fname,
                                     os.path.join(GRAPH.gp_dir, cmd),
                                     GRAPH.web_nonproc_dir, **kwargs)

        if file_list:

            MAIL = gen_class.Mail(GRAPH.emailtowarn,
                                  "Valid File Name, but Non-Processed File(s)",
                                  GRAPH.emailfrom)
            MAIL.add_2_msg("These file(s) passed name validation, but failed ")
            MAIL.add_2_msg("for another reason.  Please investigate.\n")
            MAIL.add_2_msg("Files moved to " + GRAPH.web_nonproc_dir + "\n\n")

            for fname in file_list:

                MAIL.add_2_msg(fname + "\n")
                gen_libs.write_file2(GRAPH.error_log_hdlr,
                                     "Warning: " + fname + " valid name, but" +
                                     " has failed for another reason." +
                                     "  Please investigate.")

            MAIL.send_mail()
    ###########################################################################


def process_reject_dict(GRAPH, **kwargs):

    """Function:  process_reject_dict

    Description:  Looks for any files that are in the reject dictionary and if
        detected creates an email with a list of rejected files and the
        reason for the reject.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            None

    """

    proc_flag = False

    for cmd in GRAPH.reject_dict:

        # If there are files to be processed and proc_flag is False.
        if GRAPH.reject_dict[cmd] and not proc_flag:

            MAIL = gen_class.Mail(GRAPH.emailtowarn, "GP:  Rejected files",
                                  GRAPH.emailfrom)
            MAIL.add_2_msg("File names that were not processed:\n")
            proc_flag = True

        for reject in GRAPH.reject_dict[cmd]:

            for dict_key in reject:

                MAIL.add_2_msg(dict_key + ":  " + reject[dict_key] + "\n")

    if proc_flag:
        MAIL.send_mail()


def dir_cleanup(GRAPH, **kwargs):

    """Function:  dir_cleanup

    Description:  Clean up a number of directories of old files based on the
        last modified date for the files.  The expiration day value is
        hardcoded into the function call.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            None

    """

    for cmd in GRAPH.validate_cmds:
        # Cleans the input directory of each command.
        gen_libs.file_cleanup(os.path.join(GRAPH.gp_dir, cmd), 9, **kwargs)

    # Removes old reject files after N days old.
    gen_libs.file_cleanup(GRAPH.rejected_dir, 60, **kwargs)


def process_files(GRAPH, **kwargs):

    """Function:  process_files

    Description:  Controls the processing of graph plot files.  Fetch a list of
        files, runs a number of validation checks against the files,
        creates an array of F_Graph instances which holds all of the
        information for each file in a seperate class instance.  Also
        processes rejected and non-processed files and finally runs a
        clean up of old files and directories.

    Arguments:
        (input) GRAPH -> Graph class instance.
        (input) **kwargs:
            pattern -> Regex search parameter for file names.
            ext_list -> List of allowable extensions to graphplot files.

    """

    fetch_files(GRAPH, **kwargs)

    # Are there files to process.
    if files_to_proc(GRAPH.file_dict, **kwargs):

        # Regex expr for valid file names.
        filter_file_names(GRAPH, **kwargs)

        # Are there valid files to process.
        if files_to_proc(GRAPH.filtered_file_dict, **kwargs):

            fgraph_ary = process_dir_files(GRAPH, **kwargs)

            if fgraph_ary:
                find_rejects(GRAPH, fgraph_ary, **kwargs)

                process_valid_files(GRAPH, fgraph_ary, **kwargs)

                # Create JSON document.
                process_fgraph_web(GRAPH, fgraph_ary, **kwargs)

            # 20160830 - Added fgraph_ary to argument list.
            find_nonproc_files(GRAPH, fgraph_ary=fgraph_ary, **kwargs)

            process_reject_dict(GRAPH, **kwargs)

            dir_cleanup(GRAPH, **kwargs)

        else:
            gen_libs.write_file2(GRAPH.error_log_hdlr,
                                 "There are no valid file names to process.")

    else:
        gen_libs.write_file2(GRAPH.error_log_hdlr,
                             "There are no files to process.")


def run_program(args_array, dir_set, file_set, prog_name, pattern, **kwargs):

    """Function:  run_program

    Description:  Loads the configuration for the program, sets up additional
        variables for the program.  Initializes the parent Graph class
        for processing of graph plot files, opens up the error log for
        writing any errors and/or warning messages to.  Validates the
        the existence and permissions for the directories and files
        required to run the program and then calls the function to
        start processing graph plot files.

    Arguments:
        (input) args_array -> Array of command line options and values.
        (input) dir_set -> Dictionary list of directories and perms.
        (input) file_set -> Dictionary list of files and perms.
        (input) prog_name -> Name of the program.
        (input) pattern -> Regex search parameter for file names.
        (input) **kwargs:
            null_dir -> List of directory variables that can be null.

    """

    try:
        PROG_LOCK = gen_class.ProgramLock(sys.argv)

        prog_cfg = gen_libs.load_module(args_array["-c"], args_array["-d"])

        pattern = pattern + "(" + "|".join(prog_cfg.file_ext) + ")"
        ext_list = ["." + x for x in prog_cfg.file_ext]

        GRAPH = system.Graph(prog_cfg=prog_cfg, prog_name=prog_name)

        if setup_validation(GRAPH, dir_set, file_set, **kwargs):

            # Is there log already open.
            if not GRAPH.error_log_hdlr:

                GRAPH.error_log_hdlr = open(GRAPH.error_abs_log, "w")

                process_files(GRAPH, pattern=pattern, ext_list=ext_list,
                              **kwargs)

            else:
                print("Error:  File {0} already open."
                      .format(GRAPH.error_abs_log))

        else:
            print("Error:  Directory or file validation failure.")

        # Close up log file and remove lock file.
        GRAPH.error_log_hdlr.close()
        GRAPH.error_log_hdlr = None

    except gen_class.SingleInstanceException:
        print("WARNING:  Lock in place for: process_graphplots")


def main():

    """Function:  main

    Description:  Initializes program-wide used variables and processes command
        line arguments and values.

    Variables:
        dir_chk_list -> contains options which will be directories.
        dir_set -> contains directories with creation option and permissions.
        file_set -> contains files with creation option and permissions.
        null_dir -> contains list of directory variables that can be null.
        opt_req_list -> contains the options that are required for the program.
        opt_val_list -> contains options which require values.
        prog_name -> contains the program name.

    Arguments:
        (input) argv -> Arguments from the command line.

    """

    dir_chk_list = ["-d"]
    dir_set = {"error_dir": {"create": True, "write": True, "read": True},
               "list_dir": {"create": False, "write": False, "read": True},
               "benum_dir": {"create": False, "write": False, "read": True},
               "graphbase_dir": {"create": True, "write": True, "read": True},
               "gp_dir": {"create": False, "write": True, "read": True},
               "metacard_dir": {"create": False, "write": True, "read": True},
               "image_dir": {"create": False, "write": True, "read": True},
               "archive_dir": {"create": False, "write": True, "read": True},
               "rejected_dir": {"create": True, "write": True, "read": True},
               "gp_meta_dir": {"create": True, "write": True, "read": True},
               "temp_dir": {"create": True, "write": True, "read": True},
               "json_dir": {"create": True, "write": True, "read": True}}
    file_set = {"tgtdeck": {"create": False, "write": False, "read": True},
                "mail_notdeck": {"create": True, "write": True, "read": True},
                "rejected_gps": {"create": True, "write": True, "read": True}}
    null_dir = ["metacard_dir", "image_dir"]
    opt_req_list = ["-c", "-d"]
    opt_val_list = ["-c", "-d"]
    prog_name = "process_graphplots.py"

    # Regex search pattern for the file name.
    dtg = "\d{8}_\d{4}Z_"
    be1 = "\d{4}[E\-]\d{5}"
    be2 = "\d{4}[A-Z]{2}\d{3,4}"
    be3 = "\d{4}[A-Z]{3}\d{3}"
    be4 = "[BDL]\d{5}"
    be5 = "DB[A-Z0-9]{4}"
    fullbe = "(" + be1 + "|" + be2 + "|" + be3 + "|" + be4 + "|" + be5 + ")"
    nomem = "_.*(._)?"
    final = "[A-Z]{2}_[A-Z]([A-Z]|[A-Z]{2}|[A-Z]{3})(_[A-Z])?."
    pattern = dtg + fullbe + nomem + final

    # Parse argument list from command line.
    args_array = arg_parser.arg_parse2(sys.argv, opt_val_list)

    if not gen_libs.help_func(args_array, __version__, help_message):
        #
        # NOTE:  Remove "not" in the below "if" before operational use.
        #
        if not gen_libs.root_run():
            if not arg_parser.arg_require(args_array, opt_req_list) \
               and not arg_parser.arg_dir_chk_crt(args_array, dir_chk_list):
                run_program(args_array, dir_set, file_set, prog_name, pattern,
                            null_dir=null_dir)

        else:
            sys.exit("Error:  Must run {0} as root".format(prog_name))


if __name__ == "__main__":
    sys.exit(main())
