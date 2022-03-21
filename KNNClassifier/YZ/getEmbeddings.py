import os
import numpy as np
import tensorflow as tf
from aeSrc.CV_IO_utils import read_imgs_dir
from aeSrc.CV_transform_utils import apply_transformer
from aeSrc.autoencoder import AutoEncoder
from aeSrc.imagetransformer import ImageTransformer
import json
import torch
import time

t0 = time.time()

# Run mode: (autoencoder -> simpleAE, convAE) or (transfer learning -> vgg19)
modelName = "convAE"  # try: "simpleAE", "convAE", "vgg19"
trainModel = False
parallel = False  # use multicore processing

inputDir = os.path.join(os.getcwd(), "outputLayoutImage")
outDir = os.path.join('/Users/XXX/Documents/Research/UsageTesting/KNNscreenClassifier/YZ/autoencoderEmbeddings', modelName)
if not os.path.exists(outDir):
    os.makedirs(outDir)

# Read images
extensions = [".jpg", ".jpeg"]

print("Reading images from outputLayoutImage'{}'...".format(inputDir))
imgs_all_with_names = read_imgs_dir(inputDir, extensions, parallel=parallel)


imgs_all = [tup[0] for tup in imgs_all_with_names]
namesToPrint = [tup[1] for tup in imgs_all_with_names]
with open('AllNames.json', 'w') as f:
    json.dump(namesToPrint, f)

shape_img = imgs_all[0].shape

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


# Print some model info
print("input_shape_model = {}".format(input_shape_model))
print("output_shape_model = {}".format(output_shape_model))



# Apply transformations to all images
transformer = ImageTransformer(shape_img_resize)

print("Applying image transformer to all resized images...")
imgs_all_transformed = apply_transformer(imgs_all, transformer, parallel=parallel)

X_all = np.array(imgs_all_transformed).reshape((-1,) + input_shape_model)
print(" -> X_all.shape = {}".format(X_all.shape))


# Train (if necessary)
if modelName in ["simpleAE", "convAE"]:
    if trainModel:
        model.compile(loss="binary_crossentropy", optimizer="adam")
        model.fit(X_all, n_epochs=n_epochs, batch_size=256)
        model.save_models()
    else:
        model.load_models(loss="binary_crossentropy", optimizer="adam")



print("Inferencing embeddings using pre-trained model...")
E_all = model.predict(X_all)
E_all_flatten = E_all.reshape((-1, np.prod(output_shape_model)))

torch.save(E_all_flatten, 'AllEmbeddings')

print(" -> E_all.shape = {}".format(E_all.shape))
