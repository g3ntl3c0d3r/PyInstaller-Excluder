# Pyinstaller-Excluder
A simple tool to reduce the size of an application you want to build with Pyinstaller by simply excluding unnecessary modules

## How does it work?
1. Gets path to the python script from user
2. Searches for imported modules in the script
3. Searches for dependencies of the imported modules
4. Marks all installed modules for exclusion except those found in the code and their dependencies
5. Generates "--exclude-module" commands and prints them

There is also an option at the end to remove some modules from the excluded list and generate the commands again in case it turns out your application requires some modules that have been excluded.
