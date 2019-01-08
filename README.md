# Python project for processing imagery graph plot files.
# Classification (U)

# Description:
  This program consists of a number of Python files to processes imagery graph plot files, this will include checking files for correct format, valifiating information in the file, and prepare the document for processing.


###  This README file is broken down into the following sections:
 * Features
 * Prerequisites
 * Installation
 * Configuration
 * Program Description
 * Program Help Function
 * Help Message
 * Testing
   - Unit
   - Integration
   - Blackbox


# Features:
  * Checking the filename to see it is valid and in the correct format.
  * Ensure the file has been added to the target deck.
  * Has a valid BE number assigned to it.
  * File is processed for the imagery process.
  * Create JSON document from the file. (Future)
  * Insert JSON document into Mongo for web applications to create web pages from. (Future)

* Prerequisites:

  * List of Linux packages that need to be installed on the server.
    - python-libs
    - python-devel
    - git
    - python-pip

  * Local class/library dependencies within the program structure.
    - lib/system
    - lib/gen_class
    - lib/arg_parser
    - lib/gen_libs


# Installation:

Install these programs using git.
  * Replace **{Python_Project}** with the baseline path of the python program.

```
umask 022
cd <Python_Project>
git clone git@sc.appdev.proj.coe.ic.gov:JAC-DSXD/process-graphplots.git
```

Install/upgrade system modules.

```
cd process-graphplots
sudo bash
umask 022
pip install -r requirements.txt --upgrade --trusted-host pypi.appdev.proj.coe.ic.gov
exit
```

Install supporting classes and libraries.

```
pip install -r requirements-python-lib.txt --target lib --trusted-host pypi.appdev.proj.coe.ic.gov
```

# Configuration:
  * Replace **{Python_Project}** with the baseline path of the python program.

Create configuration file.

```
cd config
cp graphplots.py.TEMPLATE graphplots.py
```

Make the appropriate change to the MySQL environment.  See program help message for a description on each of these 
  * validate_cmds = ["command_dir", "command_dir", ...]
  * process_cmds = ["command_dir", "command_dir", ...]
  * error_dir = "/Directory Path"
  * temp_dir = "/Directory Path"
  * list_dir = "/Directory Path"
  * graphbase_dir = "/Directory Path"
  * gp_dir = "/Directory Path"
  * archive_dir = "/Directory Path"
  * json_dir = "/Directory Path"
  * be_folder = "Directory Name"
  * rejected_folder = "Directory Name"
  * gp_meta_folder = "Directory Name"
  * web_nonproc_folder = "Directory Name"
  * tgtdeck_file = "Target Deck File"
  * mail_notdeck_file = "Mail Not In Deck File"
  * gp_reject_file = "Graph Plot Reject File"
  * metacard_dir = "/Directory Path"
  * image_dir = "/Directory Path"
  * emailfrom = "Email@From_Address"
  * emailtowarn = "Email@To_Address, ..."
  * emailtotgt = "Email@To_Address, ..."
  * img_id = Imagery User ID
  * img_grp = Imagery Group ID
  * web_id = Web User ID
  * web_grp = Web Group ID
  * f_perm = 0NNN
  * d_perm = 0NNN

```
vim graphplots.py
```


# Program Descriptions:
### Program: process_graphplots.py
##### Description: Processes imagery graph plot files.


# Program Help Function:

  All of the programs, except the command and class files, will have an -h (Help option) that will show display a help message for that particular program.  The help message will usually consist of a description, usage, arugments to the program, example, notes about the program, and any known bugs not yet fixed.  To run the help command:
  * Replace **{Python_Project}** with the baseline path of the python program.

```
{Python_Project}/process-graphplots/process_graphplots.py -h
```


# Help Message:
  Below is the help message for each of the programs along with the current version for the program.  Recommend running the -h option on the command line to ensure you have the latest help message for the program.

    Program:  process_graphplots.py

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


# Testing:

# Unit Testing:

### Description: Testing consists of unit testing for the functions in the process_graphplots.py program.

### Installation:

Install these programs using git.
  * Replace **{Python_Project}** with the baseline path of the python program.
  * Replace **{Branch_Name}** with the name of the Git branch being tested.  See Git Merge Request.

```
umask 022
cd <Python_Project>
git clone --branch {Branch_Name} git@sc.appdev.proj.coe.ic.gov:JAC-DSXD/process-graphplots.git
```

Install/upgrade system modules.

```
cd process-graphplots
umask 022
pip install -r requirements.txt --upgrade --trusted-host pypi.appdev.proj.coe.ic.gov
exit
```

Install supporting classes and libraries.

```
pip install -r requirements-python-lib.txt --target lib --trusted-host pypi.appdev.proj.coe.ic.gov
```


# Unit test runs for process_graphplots.py:
  * Replace **{Python_Project}** with the baseline path of the python program.

```
cd {Python_Project}/process-graphplots
```

### Unit:  help_message
```
test/unit/process_graphplots/help_message.py
```

### Unit:  
```
test/unit/process_graphplots/
```

### Unit:  
```
test/unit/process_graphplots/
```

### Unit:  run_program
```
test/unit/process_graphplots/run_program.py
```

### Unit:  main
```
test/unit/process_graphplots/main.py
```

### All unit testing
```
test/unit/process_graphplots/unit_test_run.sh
```

### Code coverage program
```
test/unit/process_graphplots/code_coverage.sh
```


# Integration Testing:

### Description: Testing consists of integration testing of functions in the process_graphplots.py program.

### Installation:

Install these programs using git.
  * Replace **{Python_Project}** with the baseline path of the python program.
  * Replace **{Branch_Name}** with the name of the Git branch being tested.  See Git Merge Request.

```
umask 022
cd {Python_Project}
git clone --branch {Branch_Name} git@sc.appdev.proj.coe.ic.gov:JAC-DSXD/process-graphplots.git
```

Install/upgrade system modules.

```
cd process-graphplots
sudo bash
umask 022
pip install -r requirements.txt --upgrade --trusted-host pypi.appdev.proj.coe.ic.gov
exit
```

Install supporting classes and libraries.
```
pip install -r requirements-python-lib.txt --target lib --trusted-host pypi.appdev.proj.coe.ic.gov
```

### Configuration:

Create configuration file.

```
cd test/integration/process_graphplots/config
cp graphplots.py.TEMPLATE graphplots.py
```

Make the appropriate change to the MySQL environment.  See program help message for a description on each of these 
  * validate_cmds = ["command_dir", "command_dir", ...]
  * process_cmds = ["command_dir", "command_dir", ...]
  * error_dir = "/Directory Path"
  * temp_dir = "/Directory Path"
  * list_dir = "/Directory Path"
  * graphbase_dir = "/Directory Path"
  * gp_dir = "/Directory Path"
  * archive_dir = "/Directory Path"
  * json_dir = "/Directory Path"
  * be_folder = "Directory Name"
  * rejected_folder = "Directory Name"
  * gp_meta_folder = "Directory Name"
  * web_nonproc_folder = "Directory Name"
  * tgtdeck_file = "Target Deck File"
  * mail_notdeck_file = "Mail Not In Deck File"
  * gp_reject_file = "Graph Plot Reject File"
  * metacard_dir = "/Directory Path"
  * image_dir = "/Directory Path"
  * emailfrom = "Email@From_Address"
  * emailtowarn = "Email@To_Address, ..."
  * emailtotgt = "Email@To_Address, ..."
  * img_id = Imagery User ID
  * img_grp = Imagery Group ID
  * web_id = Web User ID
  * web_grp = Web Group ID
  * f_perm = 0NNN
  * d_perm = 0NNN

```
vim graphplots.py
```

# Integration test runs for process_graphplots.py:
  * Replace **{Python_Project}** with the baseline path of the python program.

```
cd {Python_Project}/process-graphplots
```

### Integration:  
```
test/integration/process_graphplots/
```

### All integration testing
```
test/integration/process_graphplots/integration_test_run.sh
```

### Code coverage program
```
test/integration/process_graphplots/code_coverage.sh
```


# Blackbox Testing:

### Description: Testing consists of blackbox testing of the process_graphplots.py program.

### Installation:

Install the project using git.
  * Replace **{Python_Project}** with the baseline path of the python program.
  * Replace **{Branch_Name}** with the name of the Git branch being tested.  See Git Merge Request.

```
umask 022
cd {Python_Project}
git clone --branch {Branch_Name} git@sc.appdev.proj.coe.ic.gov:JAC-DSXD/process-graphplots.git
```

Install/upgrade system modules.

```
cd process-graphplots
sudo bash
umask 022
pip install -r requirements.txt --upgrade --trusted-host pypi.appdev.proj.coe.ic.gov
exit
```

Install supporting classes and libraries.
```
pip install -r requirements-python-lib.txt --target lib --trusted-host pypi.appdev.proj.coe.ic.gov
```

### Configuration:

Create configuration file.
```
cd test/blackbox/process_graphplots/config
cp graphplots.py.TEMPLATE graphplots.py
```

Make the appropriate change to the MySQL environment.  See program help message for a description on each of these 
  * validate_cmds = ["command_dir", "command_dir", ...]
  * process_cmds = ["command_dir", "command_dir", ...]
  * error_dir = "/Directory Path"
  * temp_dir = "/Directory Path"
  * list_dir = "/Directory Path"
  * graphbase_dir = "/Directory Path"
  * gp_dir = "/Directory Path"
  * archive_dir = "/Directory Path"
  * json_dir = "/Directory Path"
  * be_folder = "Directory Name"
  * rejected_folder = "Directory Name"
  * gp_meta_folder = "Directory Name"
  * web_nonproc_folder = "Directory Name"
  * tgtdeck_file = "Target Deck File"
  * mail_notdeck_file = "Mail Not In Deck File"
  * gp_reject_file = "Graph Plot Reject File"
  * metacard_dir = "/Directory Path"
  * image_dir = "/Directory Path"
  * emailfrom = "Email@From_Address"
  * emailtowarn = "Email@To_Address, ..."
  * emailtotgt = "Email@To_Address, ..."
  * img_id = Imagery User ID
  * img_grp = Imagery Group ID
  * web_id = Web User ID
  * web_grp = Web Group ID
  * f_perm = 0NNN
  * d_perm = 0NNN

```
vim graphplots.py
```

# Blackbox test run for process_graphplots.py:
  * Replace **{Python_Project}** with the baseline path of the python program.

### Blackbox:  
```
cd {Python_Project}/process-graphplots
test/blackbox/process_graphplots/blackbox_test.sh
```

