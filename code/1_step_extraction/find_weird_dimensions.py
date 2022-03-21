# Importing Image class from PIL module
from PIL import Image
import os

sourceFile = open('Weird Dimensions.txt', 'w')

usage_root_dir = r"C:\Users\Arthur\Documents\Combined" #change this directory to wherever the Combined folder is
folders = [folder for folder in os.listdir(usage_root_dir) if os.path.isdir(os.path.join(usage_root_dir, folder)) and not folder.startswith('.')]

#loop over folders to find the images with weird dimension sizes

counter2 = 0
for folder in folders:
    nextPath = usage_root_dir + "/" + folder
    folders2 = [folder for folder in os.listdir(nextPath) if os.path.isdir(os.path.join(nextPath, folder)) and not folder.startswith('.')]
    for folder2 in folders2:
        nextPath2 = nextPath + "/" + folder2
        folders3 = [folder for folder in os.listdir(nextPath2) if os.path.isdir(os.path.join(nextPath2, folder)) and not folder.startswith('.')]
        for folder3 in folders3:
            finalPath = nextPath2 + "/ir_data_auto"
            files = os.listdir(finalPath)
            for file in files:
                if 'screen.jpg' in file:
                    image = os.path.join(finalPath, file)
                    im = Image.open(image)
                    # Size of the image in pixels (size of original image)
                    width, height = im.size

                    if width != 1080 or height != 1920:
                        print(folder, end="/", file=sourceFile)
                        print(folder2, end="    ", file=sourceFile)
                        print(file, end=": (", file=sourceFile)
                        print(width, end=" x ", file=sourceFile)
                        print(height, end=")", file=sourceFile)
                        print("", file=sourceFile)
                        counter2 += 1
print("Number of files with weird sizes: ", end="", file=sourceFile)
print(counter2, file=sourceFile)
sourceFile.close()
