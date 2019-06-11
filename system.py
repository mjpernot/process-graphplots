# Classification (U)

"""Program:  system.py

    Description:  Class holding server system definitions.

    NOTE:  This module has been deprecated.

    Classes:
        FGraph
        System
            Graph

"""

# Libraries and Global Variables

# Standard
import sys
import smtplib
import yum
import socket
import os
import datetime
import re

# Local
import gen_libs
import version

# Version
__version__ = version.__version__


class FGraph(object):

    """Class:  FGraph

    Description:  Class which is a representation of a file in the graph plot
        process.  A file graph object is used as a proxy for file name graph
        plots.

    Super-Class:  object

    Sub-Classes:

    Methods:
        __init__ -> Class instance initilization.
        add_to_loc -> Add file name and path as dictionary format to a list.
        del_from_loc -> Remove file name and path dictionary from list
        upd_to_loc -> Update file name and path in dictionary format in a list.
        set_dirs -> Set the processing directory locations.
        set_processed -> Set attribute to say the file has been processed.
        set_xml -> Set attribute to say that a XML file exists.

    """

    def __init__(self, fname, cmd, tgtdeck, path):

        """Method:  __init__

        Description:  Initialization of an instance of the FGraph class.

        Arguments:
            (input) fname -> File name.
            (input) cmd -> Name of command.
            (input) tgtdeck -> Full path and name of target deck file.
            (input) path -> File name's directory path.

        """

        self.fname = fname
        self.cmd = cmd
        self.tgtdeck = tgtdeck

        # Parse the file name.
        self.xml_fname = ".".join([self.fname, "xml"])

        # Regex replacement on file name.
        #   Reason for the underscore change is unknown - from original code.
        self.parsed_fname = re.sub(r"_NOT_IN_TARGET_DECK", "",
                                   re.sub(r"__", "_", self.fname))

        # Parse out the date, time, and BE number.
        self.f_date, self.f_time, self.f_be = self.parsed_fname.split("_")[0:3]

        # Parse out the rest of the file name following the BE number.
        self.f_restofname = "_".join(self.parsed_fname.split("_")[3:])

        # Target Name setup
        self.f_line = gen_libs.file_search(self.tgtdeck, self.f_be)

        if self.f_line:
            # Set the Target name from tgtDeck & remove any trailing newlines.
            self.tgt_name = self.f_line.split("\t")[1].strip()
        else:
            self.tgt_name = "NOT_IN_TARGET_DECK"

        # New file name.
        self.new_fname = "_".join([self.f_date, self.f_time, self.f_be,
                                   self.tgt_name, self.f_restofname])

        # Replacement in file name.
        #   Reason for RDRR change is unknown - from the original code.
        self.new_fname = re.sub(r"_RDRR", "_RDR", self.new_fname, count=1)

        # Set other attributes with the new file name.
        self.xml_file = False
        self.new_xml_fname = ".".join([self.new_fname, "xml"])
        self.new_xml_dctm_fname = ".".join([self.new_fname, "IPL", "xml"])

        # Initial file location list/dictionary attribute.
        self.file_loc_ary = [{"File": fname, "Path": os.path.join(path, cmd)}]

        # Parse dates.
        self.f_year = self.f_date[0:4]
        self.f_mon = self.f_date[4:6]

        # Processed directory locations.
        self.cc = None
        self.cc_dir = None
        self.gp_dir = None
        self.yy_dir = None
        self.mm_dir = None

        # File has been processed
        self.processed = False

    def add_file_loc(self, fname, path):

        """Method:  add_to_loc

        Description:  Add file name and path as dictionary format to a list.

        Arguments:
            (input) fname -> File name.
            (input) path -> Path name

        """

        self.file_loc_ary.append({"File": fname, "Path": path})

    def del_from_loc(self, fname, path):

        """Method:  del_from_loc

        Description:  Remove file name and path dictionary from list.

        Arguments:
            (input) fname -> File name.
            (input) path -> Path name.

        """

        self.file_loc_ary.remove({"File": fname, "Path": path})

    def upd_to_loc(self, fname, path, new_fname=None, new_path=None):

        """Method:  upd_to_loc

        Description:  Update file name and path in dictionary format in a list.

        Arguments:
            (input) fname -> File name.
            (input) path -> Path name.
            (input) new_fname -> New file name.
            (input) new_path -> New path name.

        """

        for x in self.file_loc_ary[:]:

            # Update only if both values match original arguments.
            if x["File"] == fname and x["Path"] == path:

                # If updating only one part of the dictionary, set the other
                #   part to the original value.
                if not new_fname:
                    new_fname = fname

                if not new_path:
                    new_path = path

                x.update({"File": new_fname, "Path": new_path})

    def set_dirs(self, cc, reg_dir):

        """Method:  set_dirs

        Description:  Set the processing directory locations.

        Arguments:
            (input) cc -> Country name.
            (input) reg_dir -> Region directory path.

        """

        self.cc = cc
        self.cc_dir = os.path.join(reg_dir, self.cc)
        # Reason for 'Gp' directory is unknown - part of the original code.
        self.gp_dir = os.path.join(self.cc_dir, "Gp")
        self.yy_dir = os.path.join(self.gp_dir, self.f_year)
        self.mm_dir = os.path.join(self.yy_dir, self.f_mon)

    def set_processed(self):

        """Method:  set_processed

        Description:  Set attribute to say the file has been processed.

        Arguments:

        """

        self.processed = True

    def set_xml(self):

        """Method:  fetch_update_pkgs

        Description:  Set attribute to say that a XML file exists.

        Arguments:

        """

        self.xml_file = True


class System(object):

    """Class:  System

    Description:  Class which is a representation of a Linux server.  A server
        object is used as a proxy for operating with the system.  The basic
        methods and attributes to contain information about the physical
        server.

    Super-Class:  object

    Sub-Classes:
        Graph

    Methods:
        __init__ -> Class instance initilization.
        set_host_name -> Set the hostname attribute.

    """

    def __init__(self, host=None, host_name=None):

        """Method:  __init__

        Description:  Initialization of an instance of the System class.

        Arguments:
            (input) host -> 'localhost' or IP.
            (input) host_name -> Host name of server.

        """

        self.host = host
        self.host_name = host_name

    def set_host_name(self, host_name=None):

        """Method:  set_host_name

        Description:  Set the hostname attribute either from argument or pull
            from the server.

        Arguments:
            (input) host_name -> Host name of server.

        """

        if host_name:
            self.host_name = host_name

        else:
            self.host_name = socket.gethostname()


class Graph(System):

    """Class:  Graph

    Description:  Class which is a representation of a graph plot process.  A
        graph plot object is used as a proxy for processing graph plots.

    Super-Class:  System

    Sub-Classes:

    Methods:
        __init__ -> Class instance initilization.

    """

    def __init__(self, prog_cfg, prog_name=None, host_name=None, host=None):

        """Method:  __init__

        Description:  Initialization of an instance of the Graph class.

        Arguments:
            (input) prog_cfg -> Program configuration variable.
            (input) prog_name -> Name of the OS program.
            (input) host_name -> Host name of server.
            (input) host -> 'localhost' or IP.

        """

        super(Graph, self).__init__(host, host_name)

        if not self.host_name:
            System.set_host_name(self)

        # Commands Process Control
        #   Commands in the list run against the specified code section.
        self.validate_cmds = prog_cfg.validate_cmds
        self.process_cmds = prog_cfg.process_cmds

        # Directory paths
        self.error_dir = prog_cfg.error_dir
        self.temp_dir = prog_cfg.temp_dir
        self.list_dir = prog_cfg.list_dir
        self.graphbase_dir = prog_cfg.graphbase_dir
        self.gp_dir = prog_cfg.gp_dir
        self.archive_dir = prog_cfg.archive_dir
        self.json_dir = prog_cfg.json_dir

        # Directory names (not directory paths)
        self.be_folder = prog_cfg.be_folder
        self.rejected_folder = prog_cfg.rejected_folder
        self.gp_meta_folder = prog_cfg.gp_meta_folder
        # 20160830 - Web non-processed folder name.
        self.web_nonproc_folder = prog_cfg.web_nonproc_folder

        # File names
        self.tgtdeck_file = prog_cfg.tgtdeck_file
        self.mail_notdeck_file = prog_cfg.mail_notdeck_file
        self.gp_reject_file = prog_cfg.gp_reject_file
        self.lock_file = prog_cfg.lock_file

        # Imagery Processing directories.
        #   Leave Null if no Documentum processing is required.
        self.metacard_dir = prog_cfg.metacard_dir
        self.image_dir = prog_cfg.image_dir

        # Email addresses
        self.emailfrom = prog_cfg.emailfrom
        self.emailtowarn = prog_cfg.emailtowarn
        #   Can leave Null if no Documentum processing requested.
        self.emailtotgt = prog_cfg.emailtotgt

        # User and Group IDs
        # Imagery User and Group
        self.img_id = prog_cfg.img_id
        self.img_grp = prog_cfg.img_grp
        # Web User and Group
        self.web_id = prog_cfg.web_id
        self.web_grp = prog_cfg.web_grp

        # File and Directory Perms (set in octal)
        self.f_perm = prog_cfg.f_perm
        self.d_perm = prog_cfg.d_perm

        if prog_name:
            self.prog_name = prog_name
        else:
            self.prog_name = os.path.basename(__file__)

        # Error log attributes.
        self.dtg = datetime.datetime.strftime(datetime.datetime.now(),
                                              "%Y%m%d_%H%M%S")
        self.pid = os.getpid()
        self.error_file = "_".join([self.prog_name, self.dtg, self.host_name,
                                    str(self.pid)])
        self.error_abs_log = os.path.join(self.error_dir, self.error_file)
        self.error_log_hdlr = None

        # Derived directories.
        self.benum_dir = os.path.join(self.list_dir, self.be_folder)
        self.rejected_dir = os.path.join(self.archive_dir,
                                         self.rejected_folder)
        self.gp_meta_dir = os.path.join(self.archive_dir, self.gp_meta_folder)
        self.web_nonproc_dir = os.path.join(self.archive_dir,
                                            self.web_nonproc_folder)

        # Target deck attributes.
        self.tgtdeck = os.path.join(self.benum_dir, self.tgtdeck_file)
        self.mail_notdeck = os.path.join(self.benum_dir,
                                         self.mail_notdeck_file)
        self.gp_not_in_deck = {}

        # Valid list attributes.
        self.gp_valid_list = {}

        # Rejected graphplots and directory attributes.
        self.rejected_gps = os.path.join(self.benum_dir, self.gp_reject_file)
        self.gp_rejects = []
        self.reject_dict = {}

        # JSON Document
        self.json_name = ".".join(["gp_doc", str(self.pid), self.dtg, "json"])
        self.json_doc = os.path.join(self.json_dir, self.json_name)

        # File lists attributes.
        # Raw (full) list of files.
        self.all_file_dict = {}
        # Filtered list of files on extensions.
        self.file_dict = {}
        # Filtered list of files on valid file names.
        self.filtered_file_dict = {}

        # Program lock file.
        self.lock_prog = os.path.join(self.temp_dir, self.lock_file)
