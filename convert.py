from PIL import Image
from psd_tools import PSDImage
from natsort import os_sorted
import os

def openImage(path):
    fName, fExt = os.path.splitext(path)
    if fExt == '.psd':
        return PSDImage.load(path).as_PIL()
    else:
        return Image.open(path)

def saveImage(image, folder, index, useJPEG, quality):
    if (useJPEG):
        image.save(folder + str(index) + '.jpg', 'jpeg', quality = quality, optimize = True, progressive = True)
    else:
        image.save(folder + str(index) + '.webp', 'webp', quality = quality, method = 6)

def resizeImage(image, maxSize, meanRatio, resizeType):
    width, height = image.size
    newWidth, newHeight = width, height

    if resizeType == 'both':
        if width > height:
            resizeType = 'width'
        else:
            resizeType = 'height'

    if resizeType == 'width':
        if meanRatio:
            newWidth = min(maxSize, width)
            newHeight = int(newWidth / meanRatio)
            
        elif width > maxSize:
            newWidth = maxSize
            newHeight = int(height * newWidth / width)

    if resizeType == 'height':
        if meanRatio:
            newHeight = min(maxSize, height)
            newWidth = int(newHeight * meanRatio)
        
        elif height > maxSize:
            newWidth = int(width * maxSize / height)
            newHeight = maxSize

    if (newWidth != width or newHeight != height):
        image = image.resize((newWidth, newHeight))
            
    return image

def cutInHalfImage(image):
    width, height = image.size
    leftImage = image.crop((0, 0, width / 2, height))
    rightImage = image.crop((width / 2, 0, width, height))
    return (leftImage, rightImage)


def analysePageProfile(images):
    ratios = []
    for f in images:
        image = openImage(f['path'])
        width, height = image.size
        ratios += [width / height]

    ratios.sort()

    splitPoint = (ratios[-1] + ratios[0]) / 2
    return splitPoint


def autofitCalculate(images):
    ratios = []
    for f in images:
        image = openImage(f['path'])
        width, height = image.size
        ratios += [width / height]

    ratios.sort()

    splitPoint = (ratios[-1] + ratios[0]) / 2

    groupA = [e for e in ratios if e < splitPoint]
    groupB = [e for e in ratios if e >= splitPoint]

    meanRatioA = sum(groupA) / len(groupA)
    meanRatioB = sum(groupB) / 2 / len(groupB)

    meanRatio = (meanRatioA + meanRatioB) / 2

    '''
    meanGroupA = sum(groupA) / len(groupA)
    for i, e in enumerate(meanGroupA):
        if abs(e - meanGroupA) > 0.1:
            error = "The page " + fileList[i] + ' has a ratio that highly deviates from the rest. The image would be visibly distorded if its ratio was normalized. Please verify this page yourself.'
            raise Exception(error)
    '''
            
    # Square deviations
    #deviations = [(x - meanRatio) ** 2 for x in ratios]
    # Variance
    #varianceRatio = sum(deviations) / n

    return meanRatio
