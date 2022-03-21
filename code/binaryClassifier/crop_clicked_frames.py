# Importing Image class from PIL module
from PIL import Image
import os
import glob


usage_root_dir = os.path.abspath('/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/11-Help')
# folder_to_crop = 'clicked_frames'

# dataDir = os.path.join(scriptLocation,"data") # comment this when hardcoding input, output path
# outputDir = os.path.join(dataDir,'nonKeyCrop') #put the location of output folder here
# inputDir = os.path.join(dataDir,"nonKeyboard") #put the location of folder containing input images here

'''Loop over all the .jpg files in the input location and crop to 1075*810 size. This size is chosen to crop the keyboard region.
    Saves the cropped image in outputDir'''
def crop_per_dir(inputDir, outputDir):
    files = os.listdir(inputDir)
    counter =0
    for file in files:
        if '.jpg' in file:
            counter = counter+1
            image = os.path.join(inputDir,file)
            newImage = os.path.join(outputDir,file)

            im = Image.open(image)

            # Size of the image in pixels (size of original image)
            width, height = im.size

            #resize the input to 1080*1920 if not this size originally
            if width != 1080 or height !=1920:
                newSize = (1080,1920)
                im = im.resize(newSize)

            left = 5
            top = 1920 / 2 + 150
            right = 1080
            bottom = 1920

            im1 = im.crop((left, top, right, bottom))

            im1.save(newImage)

        # Shows the image in image viewer
        # im1.show()

def generate_clicked_frame_crop(usage_root_dir):
    for sub_dir in glob.glob(usage_root_dir + '/*/clicked_frames'):
        outputDir = sub_dir + '_crop'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        crop_per_dir(sub_dir, outputDir)
        print(outputDir, 'DONE!')

if __name__ == '__main__':
    generate_clicked_frame_crop(usage_root_dir)
    print('all done! :)')
