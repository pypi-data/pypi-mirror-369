setversion
==========

Commandline tool to update version numbers in a project.

Existing tools already exist such as [bump-my-version](https://github.com/callowayproject/bump-my-version).
This tool's uniqueness is in the use of code comments to designate version strings to change.

Usage
-----

    usage: setversion.py [-h] {init,search,bump} ...
    
    Quickly change the version of stack by adjusting the compose file.
    
    positional arguments:
      {init,search,bump}  command help
        init              Create settings file to prep folder for use
        search            Search source files
        bump              Bump version
    
    options:
      -h, --help          show this help message and exit

Generate Steps to get started are:

1) Initialize a project folder (creates setversion.ini)

       $ setversion init /my/project
       Initial version: 1.0.0
       Initialized /my/project/setversion.ini

2) Find occurrences of your version string in the project

       $ cd /my/project
       $ setverion search 1.0.0

       Project:     /my/project
       
       build\lib\setversion.py[14]: VERSION='1.0.0'
       pyproject.toml[7]: version = "1.0.0"
       README.md[30]: Initial version: 1.0.0
       setversion.egg-info\PKG-INFO[3]: Version: 1.0.0
       setversion.ini[2]: current_version = 1.0.0
       setversion.py[14]: VERSION='1.0.0'

3) Modify your source files with markers

       [build-system]
       requires = ["setuptools>=61.0", "wheel"]
       build-backend = "setuptools.build_meta"
       
       [project]
       name = "setversion"
       version = "1.0.0"      # setversion      <--------------------------------------------
       description = "Quickly change the version of stack by adjusting the compose file"
       authors = [
           {name = "Nathan Shearer", email = "shearern@gmail.com"}
       ]
       readme = "README.md"
       license = {text = "MIT"}
       requires-python = ">=3.7"
       
       [project.scripts]
       setversion = "setversion:main"
       
       [tool.setuptools]
       py-modules = ["setversion"]

4) Now you can bump the version as needed

       Project:     /my/project
       Component:   default
       Current:     1.0.0
       New Version: 1.0.1
       
       pyproject.toml[7]: version = "1.0.1" # setversion
       README.md[40]: build\lib\setversion.py[14]: VERSION='1.0.1'
       README.md[44]: setversion.ini[2]: current_version = 1.0.1
       README.md[45]: setversion.py[14]: VERSION='1.0.1'
       README.md[55]: version = "1.0.1"      # setversion      <--------------------------------------------
       setversion.py[14]: VERSION='1.0.1' # setversion
       
       Continue (y/n)? y
       
       Modifying pyproject.toml
       Modifying README.md
       Modifying setversion.ini
       Modifying setversion.py
       
       Finished
