#!/usr/bin/env python

# Generates photo collage from photo cache
import argparse, random, os, heapq

from os import path
from PIL import Image

# Utility Functions
# =================

def averageImageColor(filename):
    """ Calculates average image color - taken from https://gist.github.com/olooney/1246268 """
    i = Image.open(filename)
    if i.mode == "L":
        i = i.convert(mode = "RGB")
    h = i.histogram()
 
    # split into red, green, blue
    r = h[0:256]
    g = h[256:256*2]
    b = h[256*2: 256*3]
 
    # perform the weighted average of each channel:
    # the *index* is the channel value, and the *value* is its weight
    return (
        sum( i*w for i, w in enumerate(r) ) / sum(r),
        sum( i*w for i, w in enumerate(g) ) / sum(g),
        sum( i*w for i, w in enumerate(b) ) / sum(b)
    )

def getColorFromPalette(palette, index):
    i = 3 * index
    return (ord(palette[i]), ord(palette[i + 1]), ord(palette[i + 2]))

# Collage Image
# =============

class CollageImage:
    """ An image from the cache """

    color = None
    path = None

    def __init__(self, path):
        self.path = path
        # get average color
        self.color = averageImageColor(path)

    def getCloseness(self, otherColor):
        c1 = self.color
        c2 = otherColor
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** (1 / 3.0)

    def pasteTo(self, image, coord):
        img = Image.open(self.path)
        image.paste(img, coord)

# Generation Code
# ===============

def prepareTargetImage(args):
    targetImage = Image.open(args.target)
    # Resize to target size
    width = args.targetWidth
    height = int(targetImage.size[1] * (float(width) / targetImage.size[0]))
    targetImage = targetImage.resize((width, height))

    # Change to palette
    return targetImage.convert(mode = "P")

def collectCachedImageColors(cacheDir):
    filenames = set([s for s in os.listdir(cacheDir) if s.endswith(".jpg")])
    images = []
    for filename in filenames:
        imagePath = path.join(cacheDir, filename)
        # skip empty files
        if os.stat(imagePath).st_size == 0: continue
        images.append(CollageImage(imagePath))
    return images

def assignImageToColors(image, colors, colorImages):
    def colorCloseness(tup):
        return image.getCloseness(tup[0])
    colorsCopy = colors[:]
    colorsCopy.sort(key=colorCloseness)

    for color in colorsCopy:
        imageReplaced = False
        images = colorImages[color[1]]

        if len(images) == color[2]:
            lastImage = images[0][1]
            if lastImage.getCloseness(color[0]) <= image.getCloseness(color[0]):
                continue
            # remove last image
            heapq.heappop(images)
            imageReplaced = True

        heapq.heappush(images, (-image.getCloseness(color[0]), image))

        if imageReplaced:
            # put image back in mixing bag
            assignImageToColors(lastImage, colors, colorImages)
        break


def assignImagesToColors(targetImage, images):
    palette = targetImage.palette.tobytes()
    colors = [(getColorFromPalette(palette, c), c, n) for n, c in targetImage.getcolors()]
    colorImages = dict([(c, []) for color, c, n in colors])

    for image in images: assignImageToColors(image, colors, colorImages)

    return colorImages

def generatePicture(targetImage, colorImages, thumbnailSize, outputFilename):
    width = targetImage.size[0] * thumbnailSize
    height = targetImage.size[1] * thumbnailSize
    
    newImage = Image.new('RGB', (width, height))
    for x in range(targetImage.size[0]):
        for y in range(targetImage.size[1]):
            pixel = targetImage.getpixel((x, y))
            image = colorImages[pixel].pop()[1]
            image.pasteTo(newImage, (x * thumbnailSize, y * thumbnailSize))
    newImage.save(outputFilename)

def buildCollage(args):
    print "Preparing collage..."
    targetImage = prepareTargetImage(args)

    print "Collecting cached images..."
    images = collectCachedImageColors(args.source)
    print str(len(images)) + " loaded!"
    totalPixels = targetImage.size[0] * targetImage.size[1]
    if totalPixels > len(images):
        print "Warning! There are more pixels (" + str(totalPixels) + ") than images"
        return

    print "Running image collager for " + str(totalPixels) + " pixels..."
    colorImages = assignImagesToColors(targetImage, images)
    generatePicture(targetImage, colorImages, args.size, args.output)
    print "Picture generated!"

def main():
    parser = argparse.ArgumentParser(description='Builds photo cache from Facebook/Faces of Facebook')
    parser.add_argument('target', metavar='TARGET_FILE', help="The target photo to make it look like")
    parser.add_argument('--target-width', dest='targetWidth', default='30', type=int, metavar='WIDTH', help="The target width for the image (final image will be a multiple of target width)")
    parser.add_argument('--source', dest='source', default='cache', metavar='SOURCE_DIR', help="Source directory of images (all images must be square and of equal size)")
    parser.add_argument('--size', dest='size', default='100', metavar='SIZE', type=int, help="Size of cached images (must be square so any one dimension)")
    parser.add_argument('--output', dest='output', default='output.jpg', metavar='FILE', help="Name of file to output the collage to")
    args = parser.parse_args()

    buildCollage(args)

if __name__ == '__main__':
    main()
