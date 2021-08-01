import os
import time
import sys
import math
import json
from display import *
from convert import *
from slugify import slugify
import shutil

def saveJSON(data, filePath):
    with open(filePath, 'w') as f:
        json.dump(data, f, indent = 2)

def loadJSON(filePath):
    with open(filePath, 'r') as file:
        return json.load(file)



def createTitle():
    displayTitleBox("CREATE TITLE")

    titleType = displayOptions('What type of document is it?', [e['name'] for e in types])
    titleType = types[titleType - 1]
    
    inputPath = displayQuery('Enter path to the book folder', lambda x : os.path.isdir(x), "The given path is incorrect.")
    if inputPath[-1] != '\\' and inputPath[-1] != '/': inputPath += '/'

    # -- ANALYSIS OF THE INPUT FOLDER --

    images = []

    hasFolder = False
    hasFile = False
    foldersL1 = []
    for e in os_sorted(os.listdir(inputPath)):
        if os.path.isdir(inputPath + e):
            hasFolder = True
            foldersL1 += [inputPath + e + '/']
        if os.path.isfile(inputPath + e):
            images += [{'path': inputPath + e, 'volume': 1, 'chapter': 1}]
            hasFile = True

    if not hasFolder and not hasFile:
        print(errorified('The given folder is empty. Aborting.'))
        exit()

    if hasFolder and hasFile:
        print(errorified('The given folder has subfolders and images. Aborting.'))
        exit()

    if hasFolder and not hasFile:
        option = displayOptions('There are subfolders such as: ' + ', '.join(foldersL1[:3]) + '... Are these:', ['Volumes', 'Chapters'])

        hasFolder = False
        hasFile = False
        foldersL2 = []
        for index, folderL1 in enumerate(foldersL1):
            for e in os_sorted(os.listdir(folderL1)):
                if os.path.isdir(folderL1 + e):
                    hasFolder = True
                    foldersL2 += [folderL1 + e + '/']
                if os.path.isfile(folderL1 + e):
                    hasFile = True
                    if option == 1:
                        images += [{'path': folderL1 + e, 'volume': index + 1, 'chapter': 1}]
                    else:
                        images += [{'path': folderL1 + e, 'volume': 1, 'chapter': index + 1}]

        if option == 2:
            if hasFolder:
                print(errorified('There are subfolders inside the chapters\' folder. This is not supposed to be the case. Aborting.'))
                exit()

            if not hasFile:
                print(errorified('There are no files in the chapters\' folder. Aborting.'))
                exit()

        if option == 1:
            if not hasFile and not hasFolder:
                print(errorified('The subfolders are empty. Aborting.'))
                exit()

            if hasFolder and hasFile:
                print(errorified('The subfolders have mixed content (folders and images). Aborting.'))
                exit()

            if hasFolder and not hasFile:

                hasFolder = False
                hasFile = False
                for volume, folderL1 in enumerate(foldersL1):
                    for chapter, folderL2 in enumerate(os_sorted(os.listdir(folderL1))):
                        for e in os_sorted(os.listdir(folderL1 + '/' + folderL2)):
                            if os.path.isdir(folderL1 + folderL2 + '/' + e): hasFolder = True
                            if os.path.isfile(folderL1 + folderL2 + '/' + e):
                                hasFile = True
                                images += [{'path': folderL1 + folderL2 + '/' + e, 'volume': volume + 1, 'chapter': chapter + 1}]

                if not hasFile:
                    print(errorified('The chapter-level folders are empty. Aborting.'))
                    exit()

                if hasFolder:
                    print(errorified('There are subfolders in the chapter-level folders. This is not supposed to be the case. Aborting.'))
                    exit()
   

    title = displayQuery('Enter a name for this title')
    titleSlug = slugify(title).lower()
    
    outputFolder = libraryPath + titleSlug + '/'
    if outputFolder[-1] != '\\' and outputFolder[-1] != '/': outputFolder += '/'

    overwrite = False
    if os.path.isdir(outputFolder):
        overwrite = displayYNQuery(warningfied('The folder already exist, do you want to overwrite it?'), False)
        if not overwrite: exit()

    # -- Supplementary options --
    japaneseOrder = False
    autofit = False

    if titleType['supportDoublePage']:
        japaneseOrder = displayYNQuery('Is the title in Japanese order (right page then left page)?', False)
        autofit = displayYNQuery('Enable autofit?', False)


    grayscale = displayYNQuery('Convert/keep the image B&W?', False)
    useJPEG = displayYNQuery('Use JPEG instead of WebP?', False)


    quality = displayQuery('Enter the image quality (default: 80)', lambda x : x == '' or (x.isnumeric() and int(x) >= 0 and int(x) <= 100), 'Please enter a value between 0 and 100')
    if quality:
        quality = int(quality)
    else:
        quality = 80


    if titleType['resizeType'] == 'both':
        maxSizeMessage = 'Enter the maximum size for width or height (default: 1600)'
    else:
        maxSizeMessage = 'Enter the maximum ' + titleType['resizeType'] + ' (default: 1600)'
    maxSize = displayQuery(maxSizeMessage, lambda x : x == '' or (x.isnumeric() and int(x) > 0), 'Please enter a value above 0')
    if maxSize:
        maxSize = int(maxSize)
    else:
        maxSize = 1600


    print(boldified('Selected settings:'))
    print('titleType', titleType['name'])
    print('outputFolder', outputFolder)
    print('overwrite', overwrite)
    print('supportDoublePage', titleType['supportDoublePage'])
    print('resizeType', titleType['resizeType'])
    print('maxSize', maxSize)
    print('autofit', autofit)
    print('japaneseOrder', japaneseOrder)
    print('grayscale', grayscale)
    print('useJPEG', useJPEG)
    print('quality', quality)

    if overwrite: shutil.rmtree(outputFolder)
    os.mkdir(outputFolder)

    # -- IMAGE PROCESSING & SAVING --

    print('\n')

    for fileIndex, fileImage in enumerate(images):

        print('\033[1A' + 'Progression: ' + str(fileIndex + 1) + '/' + str(len(images)))
        
        saveFolder = outputFolder + str(fileImage['volume']) + '/'
        if not os.path.isdir(saveFolder):
            currentChapter = 0
            imageIndex = 1
            os.mkdir(saveFolder)

            # Reanalyse the page profile and ratio per volume
            splitPoint = analysePageProfile(images)
            meanRatio = None
            if autofit: meanRatio = autofitCalculate(images)

            # Volume level
            data = {'bookmarks': []}
            saveJSON(data, saveFolder + 'config.json')

        if currentChapter != fileImage['chapter']:
            currentChapter = fileImage['chapter']
            data = loadJSON(saveFolder + 'config.json')
            data['bookmarks'] += [{'name':'', 'type':'chapter', 'page': imageIndex}]
            saveJSON(data, saveFolder + 'config.json')
            
        
        fName, fExt = os.path.splitext(fileImage['path'])
        image = Image.open(fileImage['path'])

        if grayscale:
            image = image.convert('L')
        width, height = image.size

        if (width / height) > splitPoint and titleType['supportDoublePage']:
            
            left, right = cutInHalfImage(image)

            if (japaneseOrder):
                firstImage = right
                secondImage = left
            else:
                firstImage = left
                secondImage = right
                
            saveImage(resizeImage(firstImage, maxSize, meanRatio, titleType['resizeType']),
                      saveFolder,
                      imageIndex,
                      useJPEG,
                      quality)
            
            imageIndex += 1
            saveImage(resizeImage(secondImage, maxSize, meanRatio, titleType['resizeType']),
                      saveFolder,
                      imageIndex,
                      useJPEG,
                      quality)
        else:
            
            saveImage(resizeImage(image, maxSize, meanRatio, titleType['resizeType']),
                      saveFolder,
                      imageIndex,
                      useJPEG,
                      quality)

        imageIndex += 1


    # -- Write the JSON files --
    data = {
      "title": title,
      "bookType": titleType['slug'],
      "numVolumes": fileImage['volume'],
      "fileExtension": ".jpg" if useJPEG else ".webp",
      "japaneseOrder": japaneseOrder
    }
    saveJSON(data, outputFolder + 'config.json')

    data = loadJSON(libraryPath + 'config.json')
    if titleSlug not in data['titles']: data['titles'] += [titleSlug]
    saveJSON(data, libraryPath + 'config.json')



# _____________________________________________________________________________

# -- START CONFIG --

types = []
types += [{'slug': 'book',      'name': 'Book',      'supportDoublePage': True,  'resizeType': 'both'}]
types += [{'slug': 'manga',     'name': 'Manga',     'supportDoublePage': True,  'resizeType': 'both'}]
types += [{'slug': 'webtoon',   'name': 'Webtoon',   'supportDoublePage': False, 'resizeType': 'width'}]
types += [{'slug': 'imageset',  'name': 'Image Set', 'supportDoublePage': False, 'resizeType': 'both'}]

# -- END CONFIG --


clearConsole()
displayAppTitle()

libraryPath = ''
if len(sys.argv) == 2: libraryPath = sys.argv[1]
if not os.path.isdir(libraryPath):
    libraryPath = displayQuery('Enter path to Okuma-Library folder', lambda x : os.path.isdir(x), "The given path is incorrect.")
if libraryPath[-1] != '\\' and libraryPath[-1] != '/': libraryPath += '/'

displayTitleBox("SELECTED LIBRARY", libraryPath)

if not os.listdir(libraryPath):
    data = {'titles': ['lol']}
    saveJSON(data, libraryPath + 'config.json')    

    
option = displayOptions('What do you want to do?', ['Create a new title', 'Modify an existing title', 'Manage or repair the library'])

if option == 1: createTitle()
    
