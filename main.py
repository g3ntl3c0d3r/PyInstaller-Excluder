from pkgutil import iter_modules
import pathlib
import pip
import sys
import os
import io


def find_dependencies(modulus):
    if modulus != '':
        if ', ' in modulus:
            mods = modulus.split(', ')
            for m in mods:
                find_dependencies(m)
        else:
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            sys.stderr = open(os.devnull, "w")
            pip.main(['show', modulus])
            sys.stderr = sys.__stderr__
            depends.append(new_stdout.getvalue())

            sys.stdout = old_stdout

            if depends[len(depends) - 1] != '':
                txt = depends[len(depends) - 1]
                depends[len(depends) - 1] = ''
                for k in range(txt.index('\nRequires: ') + 11, txt.index('\nRequired-by: ')):
                    depends[len(depends) - 1] += txt[k]

                find_dependencies(depends[len(depends) - 1])


if __name__ == '__main__':
    # Print path info
    print('\nEnter absolute or relative path to your python script')
    print('Current directory: ' + str(pathlib.Path(__file__).parent.absolute()))

    # Get source code file path
    isPathOk = False
    while not isPathOk:
        srcFilePath = input('\nPath: ')
        isPathOk = True
        try:
            srcFile = open(srcFilePath)
        except OSError:
            print('\nThis file does not exist or the path is incorrect')
            print('Please try again')
            isPathOk = False

    # Search for modules
    foundModules = []
    for line in srcFile:
        if '\'' not in line and '"' not in line and '#' not in line:
            if 'from ' in line:
                foundModules.append('')
                if '.' in line:
                    endOfLine = line.index('.')
                else:
                    endOfLine = line.index(' import')
                for i in range(line.index('from ') + 5, endOfLine):
                    foundModules[len(foundModules) - 1] += line[i]
                continue
            elif 'import ' in line:
                foundModules.append('')
                if ' as ' in line:
                    endOfLine = line.index(' as')
                elif '.' in line:
                    endOfLine = line.index('.')
                else:
                    endOfLine = len(line) - 1
                for i in range(line.index('import ') + 7, endOfLine):
                    foundModules[len(foundModules) - 1] += line[i]
                continue

    # Remove duplicates
    foundModules = list(set(foundModules))

    # Remove whitespaces
    for i in range(len(foundModules)):
        foundModules[i] = str(foundModules[i]).strip()

    # Search for dependencies of each module
    print()
    depends = []
    if len(foundModules) > 0:
        for module in foundModules:
            find_dependencies(module)

    # Remove empty elements
    depends = list(filter(None, depends))

    # Split multiple modules
    for i in range(len(depends)):
        depends[i] = depends[i].split(', ')
        for j in range(len(depends[i])):
            depends.append(depends[i][j])
    for deps in reversed(depends):
        if type(deps) is list:
            depends.remove(deps)

    # Remove duplicates
    depends = list(set(depends))

    # Print found modules and their dependencies
    if len(foundModules) == 0:
        print('No modules were found in your script')
        print('\nAll installed modules will be excluded')
    else:
        if len(foundModules) == 1:
            print('1 module was found in your script:')
            print()
            print('- ' + foundModules[0])
        else:
            print(str(len(foundModules)) + ' modules were found in your script:')
            print()
            for module in foundModules:
                print('- ', end='')
                print(*module, sep='')
            if len(depends) > 0:
                if len(depends) > 1:
                    print('\n' + str(len(depends)) + ' dependencies were found:')
                else:
                    print('\n1 dependency was found:')
                print()
                for deps in depends:
                    print('- ', end='')
                    print(*deps, sep='')
        print('\nOther installed modules will be excluded')

    # Create --exclude-module commands
    excludeCommands = ''
    ignore = False
    n = 0
    for instModule in list(iter_modules()):
        if n != 0 and foundModules.count(
                instModule.name) == 0 and 'site-packages' in instModule.module_finder.__str__():
            for deps in depends:
                if instModule.name in deps:
                    ignore = True
            if ignore:
                ignore = False
                continue
            else:
                excludeCommands += '--exclude-module ' + instModule.name + ' '
        n += 1

    # Print all --exclude-module commands
    print('\nCopy and add this to the pyinstaller command:')
    print()
    print(excludeCommands)

    # User edit choice
    isAnswerOk = False
    while not isAnswerOk:
        userInput = input('\nDo you want to remove some modules from the command list? (y/n): ')
        if userInput == 'y':
            isAnswerOk = True
            removeModules = True
        elif userInput == 'n':
            isAnswerOk = True
            removeModules = False

    if removeModules:
        print('\nEnter the modules names below separating them with whitespace')

        isModulesOk = False
        while not isModulesOk:
            # Enter modules names
            missMods = input('\nModules: ')

            # Check if modules names are correct
            missMods = missMods.split(' ')
            for m in missMods:
                if m in excludeCommands:
                    isModulesOk = True
                else:
                    print('\nNo module named "' + m + '" in the excluded modules list')

        # Remove modules from the list
        for m in missMods:
            excludeCommands = excludeCommands.replace('--exclude-module ' + m + ' ', '')

        # Print --exclude-module commands
        print('\nDone!')
        print('Copy and add this to the pyinstaller command:')
        print()
        print(excludeCommands)

    print()
