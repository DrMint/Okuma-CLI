import os
import time
import math

CLIWIDTH = 72

def displayAppTitle():
    message = '''\033[32m

  ██████╗ ██╗  ██╗██╗   ██╗███╗   ███╗ █████╗        ██████╗██╗     ██╗
 ██╔═══██╗██║ ██╔╝██║   ██║████╗ ████║██╔══██╗      ██╔════╝██║     ██║
 ██║   ██║█████╔╝ ██║   ██║██╔████╔██║███████║█████╗██║     ██║     ██║
 ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══██║╚════╝██║     ██║     ██║
 ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║██║  ██║      ╚██████╗███████╗██║
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝\033[0m
\033[2m                                    ver.1.1 | Copyright (c) 2021 DrMint
                          Okuma-Tools is licensed under the MIT License
                                  \033[4mhttps://github.com/DrMint/Okuma-Tools\033[0m

'''
    lineDisplay(message)
    
def clearConsole():
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')

def lineDisplay(string, interval=0):
    for line in string.split('\n'):
        time.sleep(interval)
        print(line)

def calculateSpacing(string):
    nbspaces = CLIWIDTH - 2 - len(string)
    spacingL = " " * math.floor(nbspaces / 2)
    spacingR = " " * math.ceil(nbspaces / 2)
    return (spacingL, spacingR)

def boldified(string):
    return '\033[32m\033[1m' + string + '\033[0m'

def faintified(string):
    return '\033[2m' + string + '\033[0m'

def warningfied(string):
    return '\033[33m' + string + '\033[0m'

def errorified(string):
    return '\033[31m' + string + '\033[0m' 

def displayTitleBox(title, message = ""):
    spacingL, spacingR = calculateSpacing(title)
    print('┌──────────────────────────────────────────────────────────────────────┐')
    print('│' + spacingL + boldified(title) + spacingR + '│')
    if (message != ""):
        spacingL, spacingR = calculateSpacing(message)
        print('│' + spacingL + message + spacingR + '│')
    print('└──────────────────────────────────────────────────────────────────────┘')

def displayQuery(query, predicat = lambda _: True, errorMessage = ''):
    response = input(query + ': ')
    while not predicat(response):
        print(errorified(errorMessage) + '\033[2A')
        response = input(query + ': \033[K')
    print('\033[K')
    return response

def displayYNQuery(query, default):
    query += ' (Y/n)' if default else ' (y/N)'
    response = displayQuery(query, lambda x: x=='' or x.lower()=='y' or x.lower()=='n', 'Please enter y or n or press enter to select the default option')

    if response == '': return default
    return response.lower() == 'y'

def displayOptions(title, options):
    print(boldified(title))
    for index, option in enumerate(options):
        print(faintified('[' + str(index + 1) + ']'), option)
    value = displayQuery('Select an option', lambda x : x.isnumeric() and int(x) - 1 in range(len(options)), 'Please enter a value between 1 and ' + str(len(options)))
    return int(value)

