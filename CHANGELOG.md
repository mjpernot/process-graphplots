# Changelog
All notable changes to this project will be documented in this file.

The format is based on "Keep a Changelog".  This project adheres to Semantic Versioning.


## [2.0.2] - 2018-10-04
### Fixed
- dctm_processing:  Removed "**kwargs" from "os.chmod" and "os.chown" calls - not required.


## [2.0.1] - 2018-10-03
### Changed
- run_program:  Replaced internal program locking mechanism with "gen_class.ProgramLock" class.
- Moved requirements2.txt -> requirements-python-lib.txt.

### Added
- config/graphplots.py.TEMPLATE:  Added template configuration file.


## [2.0.0] - 2018-05-25
Breaking Change

### Changed
- Changed "gen_libs.Chk_Crt_File" to "gen_libs.chk_crt_file" and refactored code to take into account new returning values.
- Changed "gen_libs.Chk_Crt_Dir" to "gen_libs.chk_crt_dir" and refactored code to take into account new returning values.
- Changed "gen_libs.Rename_File2" to "gen_libs.rename_file" call.
- Replaced "gen_libs.Chown" with "os.chown" call.
- Replaced "gen_libs.Chmod" with "os.chmod" call.
- Replaced "gen_libs.Close_File" with "close" call.
- Replaced "gen_libs.Open_File" with "open" call.
- Changed "gen_libs.Write_File" to "gen_libs.write_file2" call.
- Changed "gen_libs.Write_File2" to "gen_libs.write_file" call.
- Changed "gen_libs" calls to new naming schema.
- Changed "system.Mail" to "gen_class.Mail" call.
- Changed "system" calls to new naming schema.
- Changed "arg_parser" calls to new naming schema.
- Changed function names from uppercase to lowercase.
- Made program PEP-8 compliant.
- Merged version control entries into CHANGELOG file.
- Setup single-source version control.

### Added
- Added gen_class library module.

## [1.3.0] - 2018-05-24
### Added
- Moved process_graphplots.py from python_project to this project.
- setup.py:  Added setuptools module.
- version.py:  Added single-source version control.
- requirements2.txt:  Install of python library modules.
- requirements.txt:  Install of system python modules.
- README.md:  Added README file.


## [1.2.0] - 2017-08-22
### Changed
- Add classification line for Sunspear use.
- Help_Message:  Replace docstring with printing the programs __doc__.
- Change order of library sequence to be PEP-8 compliant.
- Change versioning information to be PEP-440 compliant.
- Change single quotes to double quotes to be PEP-8 compliant.
- Convert program to use local libraries from ./lib directory.
- Convert comments/documentation to docstrings.


## [1.1.0] - 2016-08-30
### Fixed
- Error fix.  The program was re-processing files that passed named validation, but failed for other reasons.  Fix looks for files that were not fully processed and handles these files.
- Find_NonProc_Files:  Checks to see if the files passed name validation, but failed for another reason.  Moves these files to non-processed directory and sends out a notification and error log entry.
- Process_Files:  Changed argument list to Find_NonProc_Files function call.
- Help_Message:  Added new entries to Help_Message.


## [1.0.0] - 2016-08-09
- Initial creation.

