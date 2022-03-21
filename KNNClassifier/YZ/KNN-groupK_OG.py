import os, sys

sys.path.append('..')

import numpy as np
import tensorflow as tf
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from aeSrc.CV_IO_utils import read_imgs_dir
from aeSrc.CV_transform_utils import apply_transformer
from aeSrc.CV_transform_utils import resize_img, normalize_img
from aeSrc.CV_plot_utils import plot_query_retrieval, plot_tsne, plot_reconstructions
from aeSrc.autoencoder import AutoEncoder
from aeSrc.imagetransformer import ImageTransformer
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import pandas as pd
import shutil
from time import sleep
from sklearn.model_selection import train_test_split
import json
import torch
from getIRLabels import getLabels,filterOutSmallCategories
from sklearn import metrics
import time
from sklearn.model_selection import GroupKFold

'''Does the split by app names'''

t0 = time.time()






# Run mode: (autoencoder -> simpleAE, convAE) or (transfer learning -> vgg19)
modelName = "convAE"  # try: "simpleAE", "convAE", "vgg19"
trainModel = False
parallel = False  # use multicore processing




# Make paths
# dataTrainDir = os.path.join(os.getcwd(), "Train-rsz-subset")
# dataTestDir = os.path.join(os.getcwd(), "Test-rsz-subset")
allFilesDir = os.path.join(os.getcwd(),"../outputLayoutImage")
outDir = os.path.join(os.getcwd(), "../output-all-rsz-subset", modelName)
if not os.path.exists(outDir):
    os.makedirs(outDir)




# Read images
extensions = [".jpg", ".jpeg"]


# print("Reading train images from '{}'...".format(dataTrainDir))
# imgs_train = read_imgs_dir(dataTrainDir, extensions, parallel=parallel)
# print("Reading test images from '{}'...".format(dataTestDir))
# imgs_test = read_imgs_dir(dataTestDir, extensions, parallel=parallel)
print("Reading images from outputLayoutImage'{}'...".format(allFilesDir))
imgs_all_with_names = read_imgs_dir(allFilesDir, extensions, parallel=parallel)



allImageName = [tup[1] for tup in imgs_all_with_names]

allLabels = []
problemImages = []
#Kesina added
labelMap = getLabels()

def getLabelOfImage(labelMap,image):
    imageName = image.split("/")[-1]#.split('.jpg')[0]+"-screen.jpg" # Need to change <path>/buzzfeed-signup-1-bbox-1808.jpg to buzzfeed-signup-1-bbox-1808-screen.jpg
    # imageName= imageName.replace('-long','')
    if labelMap.get(imageName):
        label = labelMap[imageName]
        return label
    else:
        return False

# problemIndex = 0
# print(str(len(allImageName)),str(len(allLabels)),str(len(imgs_all_with_names)))
for num, imageName in enumerate(allImageName):
    filters = filterOutSmallCategories()
    label = getLabelOfImage(labelMap,imageName)
    if label and label not in filters:
        allLabels.append(label)
    else:
        problemImages.append(num)









def removeUnWantedEntries(allImageInfo):
    tempHolder=[]
    for index, info in enumerate(allImageInfo):
        if index not in problemImages:
            tempHolder.append(info)
    return tempHolder

tempCopy = imgs_all_with_names.copy()
imgs_all_with_names = removeUnWantedEntries(tempCopy)

allAppNames = []

allImageNameAfterFiltering = [tup[1] for tup in imgs_all_with_names]


for names in allImageNameAfterFiltering:
    apps = names.split("/")[-1].split('-')[0]
    allAppNames.append(apps.lower())
    # print(names, apps)

print(str(len(allImageName)),"Started with these images")
print(str(len(labelMap)),"Total labelMap")
print(str(len(problemImages)),"images with bad labels")
print(str(len(allLabels)),"Good labels")
print(str(len(allImageNameAfterFiltering)),"good image count")
print(str(len(allAppNames)),"good app names count")

# sys.exit()




imgs_all = [tup[0] for tup in imgs_all_with_names]
namesToPrint = [tup[1] for tup in imgs_all_with_names]
with open('names.json', 'w') as f:
    json.dump(namesToPrint, f)

shape_img = imgs_all[0].shape
# print("Image shape = {}".format(shape_img))

# imgs_train_all, imgs_test_all= train_test_split( imgs_all_with_names, test_size = 0.2,stratify=allLabels)



# Build models
if modelName in ["simpleAE", "convAE"]:

    # Set up autoencoder
    info = {
        "shape_img": shape_img,
        "autoencoderFile": os.path.join(outDir, "{}_autoecoder.h5".format(modelName)),
        "encoderFile": os.path.join(outDir, "{}_encoder.h5".format(modelName)),
        "decoderFile": os.path.join(outDir, "{}_decoder.h5".format(modelName)),
    }
    model = AutoEncoder(modelName, info)
    model.set_arch()

    if modelName == "simpleAE":
        shape_img_resize = shape_img
        input_shape_model = (model.encoder.input.shape[1],)
        output_shape_model = (model.encoder.output.shape[1],)
        n_epochs = 300
    elif modelName == "convAE":
        shape_img_resize = shape_img
        input_shape_model = tuple([int(x) for x in model.encoder.input.shape[1:]])
        output_shape_model = tuple([int(x) for x in model.encoder.output.shape[1:]])
        n_epochs = 500
    else:
        raise Exception("Invalid modelName!")

elif modelName in ["vgg19"]:

    # Load pre-trained VGG19 model + higher level layers
    print("Loading VGG19 pre-trained model...")
    model = tf.keras.applications.VGG19(weights='imagenet', include_top=False,
                                        input_shape=shape_img)
    model.summary()

    shape_img_resize = tuple([int(x) for x in model.input.shape[1:]])
    input_shape_model = tuple([int(x) for x in model.input.shape[1:]])
    output_shape_model = tuple([int(x) for x in model.output.shape[1:]])
    n_epochs = None

else:
    raise Exception("Invalid modelName!")

def printLoading(percentage):
    message="Completed "+str(percentage)+"%"
    sys.stdout.write('\r')
    sys.stdout.write(message)
    sys.stdout.flush()
    sleep(0.0001)

# Print some model info
print("input_shape_model = {}".format(input_shape_model))
print("output_shape_model = {}".format(output_shape_model))



# Apply transformations to all images
transformer = ImageTransformer(shape_img_resize)




print(transformer)



print("Applying image transformer to all resized images...")
imgs_all_transformed = apply_transformer(imgs_all, transformer, parallel=parallel)
X_all = np.array(imgs_all_transformed).reshape((-1,) + input_shape_model) # Convert images to numpy array
print(" -> X_all.shape = {}".format(X_all.shape))

print("Inferencing embeddings using pre-trained model...")
E_all = model.predict(X_all)
E_all_flatten = E_all.reshape((-1, np.prod(output_shape_model)))

torch.save(E_all_flatten, 'embeddings')

print(" -> E_all.shape = {}".format(E_all.shape))

gkf = GroupKFold(n_splits=18)

for train_index,test_index in gkf.split(imgs_all_with_names, allLabels, groups=allAppNames):
    # print("%s %s" % (imgs_train_all, imgs_test_all))
    # break
    # imgs_train_all =
    imgs_train_all = [imgs_all_with_names[i] for i in train_index]
    imgs_test_all = [imgs_all_with_names[i] for i in test_index]

    imgs_train_names = [tup[1] for tup in imgs_train_all]
    imgs_test_names = [tup[1] for tup in imgs_test_all]
    appName = imgs_test_names[0].split("/")[-1].split("-")[0]
    print(appName,"------------------------------------------------")

    imgs_train = [tup[0] for tup in imgs_train_all]
    imgs_test = [tup[0] for tup in imgs_test_all]



    # print("Applying image transformer to train and test images...")
    imgs_train_transformed = apply_transformer(imgs_train, transformer, parallel=parallel) #Kesina's change
    imgs_test_transformed = apply_transformer(imgs_test, transformer, parallel=parallel) #Kesina's change

    # Convert images to numpy array
    X_train = np.array(imgs_train_transformed).reshape((-1,) + input_shape_model) #Kesina changed
    X_test = np.array(imgs_test_transformed).reshape((-1,) + input_shape_model) #Kesina changed
    # print(" -> X_train.shape = {}".format(X_train.shape))
    # print(" -> X_test.shape = {}".format(X_test.shape))



    # Train (if necessary)
    if modelName in ["simpleAE", "convAE"]:
        if trainModel:
            model.compile(loss="binary_crossentropy", optimizer="adam")
            model.fit(X_all, n_epochs=n_epochs, batch_size=256)
            model.save_models()
        else:
            model.load_models(loss="binary_crossentropy", optimizer="adam")


    # Create embeddings using model
    # print("Inferencing embeddings using pre-trained model...")
    E_train = model.predict(X_train)
    E_train_flatten = E_train.reshape((-1, np.prod(output_shape_model)))
    E_test = model.predict(X_test)
    E_test_flatten = E_test.reshape((-1, np.prod(output_shape_model)))

    # print(" -> E_train.shape = {}".format(E_train.shape))
    # print(" -> E_test.shape = {}".format(E_test.shape))
    # print(" -> E_train_flatten.shape = {}".format(E_train_flatten.shape))
    # print(" -> E_test_flatten.shape = {}".format(E_test_flatten.shape))






    # if modelName in ["simpleAE", "convAE"]:
    #     print("Visualizing database image reconstructions...")
    #     imgs_all_reconstruct = model.decoder.predict(E_all)
    #     if modelName == "simpleAE":
    #         imgs_all_reconstruct = imgs_all_reconstruct.reshape((-1,) + shape_img_resize)
    #     plot_reconstructions(imgs_all, imgs_all_reconstruct,
    #                          os.path.join(outDir, "{}_reconstruct.png".format(modelName)),
    #                          range_imgs=[0, 255],
    #                          range_imgs_reconstruct=[0, 1])





    # imgs_names = [tup[1] for tup in imgs_all_with_names]





    # Fit kNN model on training images
    print("Fitting k-nearest-neighbour model on training images...")
    knn = NearestNeighbors(n_neighbors=5, metric="cosine")
    knn.fit(E_train_flatten)


    resultHolder ={}

    # Perform image retrieval on test images

    testLabels =[]
    predictedLabels =[]

    print("Performing image retrieval on test images...")
    for i, emb_flatten in enumerate(E_test_flatten):
        _, indices = knn.kneighbors([emb_flatten]) # find k nearest train neighbours
        img_query = imgs_test[i] # query image
        queryImageName = imgs_test_names[i]
        imgs_retrieval = [imgs_train[idx] for idx in indices.flatten()] # retrieval images
        topFiveMatchNames = [imgs_train_names[idx] for idx in indices.flatten()]
        labelOfQueryImage = getLabelOfImage(labelMap,queryImageName)
        closestMatchLabel  =  getLabelOfImage(labelMap,topFiveMatchNames[0])
        resultHolder[queryImageName] = topFiveMatchNames

        if labelOfQueryImage and closestMatchLabel:
            testLabels.append(labelOfQueryImage)
            predictedLabels.append(closestMatchLabel)
        # outFile = os.path.join(outDir, "{}_retrieval_{}.png".format(modelName, i))
        # plot_query_retrieval(img_query, imgs_retrieval, outFile)

    t1 = time.time()

    total = t1-t0
    print('Time taken to predict '+str(len(imgs_test))+' images '+str(total))

    #Kesina added
    score = metrics.accuracy_score(testLabels, predictedLabels)
    resultHolder["time"] = total
    resultHolder["score"] = score
    # print(metrics.accuracy_score(testLabels, predictedLabels))

    badResultCounter = {}
    for num,i in enumerate(testLabels):
        # if num ==11:
        #     break
        if testLabels[num] != predictedLabels[num]:
            if badResultCounter.get(testLabels[num]):
                badResultCounter[testLabels[num]] =badResultCounter[testLabels[num]]+1
            else:
                badResultCounter[testLabels[num]]=1
            print(testLabels[num],predictedLabels[num])

    print(badResultCounter)

    with open('predictionResult-'+appName+'-'+str(total)+'.json','w') as f:
        json.dump(resultHolder,f)
