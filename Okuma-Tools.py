import os
import sys
import argparse
import shutil
from PIL import Image
import json

def saveJSON(data, filePath):
    with open(filePath, 'w') as f:
        json.dump(data, f, indent = 2)

def loadJSON(filePath):
    with open(filePath, 'r') as file:
        return json.load(file)

def saveImage(image, folder):
    global INDEX
    INDEX += 1
    if (useJPEG):
        image.save(folder + str(INDEX) + '.jpg', 'jpeg', quality = quality, optimize = True, progressive = True)
    else:
        image.save(folder + str(INDEX) + '.webp', 'webp', quality = quality, method = method)

def resizeImage(f, image):
    width, height = image.size
    if height > maxHeight:
        if autofit:
            newWidth = int(maxHeight * meanRatio)
            newHeight = maxHeight
        else:
            newWidth = int(width * maxHeight / height)
            newHeight = maxHeight
        image = image.resize((newWidth, newHeight))
        print(f, 'is too big. Resizing to', newWidth, 'x', newHeight)
    else:
        if autofit:
            newWidth = int(height * meanRatio)
            image = image.resize((newWidth, height))
    return image

def cutInHalfImage(image):
    width, height = image.size
    leftImage = image.crop((0, 0, width / 2, height))
    rightImage = image.crop((width / 2, 0, width, height))
    return (leftImage, rightImage)


INDEX = 0
def main():

    titleFolder = libraryFolder + bookSlug + '/'
    volumeFolder = titleFolder + '1/'
    chapterFolder = volumeFolder + '1/'

    libraryJSON = libraryFolder + 'config.json' 
    titleJSON = titleFolder + 'config.json'
    volumeJSON = volumeFolder + 'config.json'


    # Create the folders
    if not os.path.isdir(libraryFolder): os.mkdir(libraryFolder)
    os.mkdir(titleFolder)
    os.mkdir(volumeFolder)
    os.mkdir(chapterFolder)

    # Create the files
    if os.path.isfile(libraryJSON):
        libraryConfig = loadJSON(libraryJSON)
        if bookSlug not in libraryConfig["titles"]:
            libraryConfig["titles"] += [bookSlug]
    else:
        libraryConfig = {}
        libraryConfig["titles"] = [bookSlug]
    saveJSON(libraryConfig, libraryJSON)

    titleConfig = {}
    titleConfig['title']            = inputFolder[:-1]
    titleConfig['bookType']         = 'book'
    titleConfig['numVolumes']       = 1
    titleConfig['fileExtension']    = '.jpg' if useJPEG else '.webp'
    #titleConfig['japaneseOrder']    = 'false'
    saveJSON(titleConfig, titleJSON)
    
    for f in os.listdir(inputFolder):
        fName, fExt = os.path.splitext(f)
        image = Image.open(inputFolder + f)
        if grayscale:
            image = image.convert('L')
        width, height = image.size

        if width > height and not noDoublePage:
            print(f + ' is double page')
            left, right = cutInHalfImage(image)
            saveImage(resizeImage(f, left), chapterFolder)
            saveImage(resizeImage(f, right), chapterFolder)
        else:
            print(f + ' is a normal page')
            saveImage(resizeImage(f, image), chapterFolder)


    volumeConfig = {}
    volumeConfig["numPages"]            = [INDEX]
    #volumeConfig["fistPageSingle"]      = 'true'
    #volumeConfig["preferDoublePage"]    = 'true'
    #volumeConfig["allowDoublePage"]     = 'true'
    saveJSON(volumeConfig, volumeJSON)
    

parser = argparse.ArgumentParser(prog='Okuma-Tools', description='A collection of tools to manage your Okuma-Library.')
parser.add_argument('sourceFolder', metavar='SOURCE_FOLDER', type=str, help='the source folder including the images of the book to convert')
parser.add_argument('libraryFolder', metavar='LIBRARY_FOLDER', type=str, help='the library folder. If it doesn\'t exist, creates it.')
parser.add_argument('slug', metavar='SLUG', type=str, help='the name of the folder used in the LIBRARY_FOLDER. I.e. my-book-title')
parser.add_argument("--quality", nargs=1, default=[80], type=int, help="a smaller value gives smaller images but introduces compression artifacts. Must be a integer between 1-100, Default is 80")
parser.add_argument("--height", nargs=1, default=[1600], type=int, help="define the maximum height for the images. Default is 1600 (px)")
parser.add_argument("--jpg", help="force the use of the file format JPEG. By default, the images are encoded in WebP.", action="store_true")
parser.add_argument("--gray", help="force the images to be in grayscale mode", action="store_true")
parser.add_argument("--force", help="if the given SLUG already exists, it will forcefully replace it.", action="store_true")
parser.add_argument("--autofit", help="force the image ratio to be the same for all pages. Can deform images slightly.", action="store_true")
parser.add_argument("--nodoublepage", help="doesn't split pages in two parts when the image is in landscape mode", action="store_true")
args = parser.parse_args()



inputFolder = args.sourceFolder
if inputFolder[-1] != '\\' and inputFolder[-1] != '/': inputFolder += '/'
libraryFolder = args.libraryFolder
if libraryFolder[-1] != '\\' and libraryFolder[-1] != '/': libraryFolder += '/'


bookSlug = args.slug
useJPEG = args.jpg
quality = args.quality[0]
maxHeight = args.height[0]
grayscale = args.gray
method = 6
force = args.force
autofit = args.autofit
noDoublePage = args.nodoublepage

if not os.path.isdir(inputFolder):
    error = "The given SOURCE_FOLDER doesn\'t exist."
    raise Exception(error)

if quality < 1 or quality > 100:
    error = "The given quality isn't valid. The quality should be an integer between 1 and 100."
    raise Exception(error)

if os.path.isdir(libraryFolder + bookSlug + '/'):
    if force:
        shutil.rmtree(libraryFolder + bookSlug + '/')
    else:
        error = "The given book slug already exists. Try a diffent slug. If you are trying to update an existing book, you can use the --force option."
        raise Exception(error)

print('\n')
print('Selected quality:', quality)
print('Selected format:', 'JPEG' if useJPEG else 'WebP')
print('Selected maxHeight:', maxHeight)
print('Selected grayscale:', grayscale)
print('\n')


if autofit:

    print('Autofit option enabled:')

    ratios = []
    fileList = os.listdir(inputFolder)
    for f in fileList:
        image = Image.open(inputFolder + f)
        width, height = image.size
        if width > height:
            ratios += [width / 2 / height]
        else:
            ratios += [width / height]

    n = len(ratios)
    # Mean of the data
    meanRatio = sum(ratios) / n

    for i, e in enumerate(ratios):
        if abs(e - meanRatio) > 0.1:
            error = "The page " + fileList[i] + ' has a ratio that highly deviates from the rest. The image would be visibly distorded if its ratio was normalized. Please verify this page yourself.'
            raise Exception(error)

            
    # Square deviations
    deviations = [(x - meanRatio) ** 2 for x in ratios]
    # Variance
    varianceRatio = sum(deviations) / n


    print('Mean ratio:', meanRatio)
    print('Variance ratio:', varianceRatio)
    print('\n')  
    

main()


















