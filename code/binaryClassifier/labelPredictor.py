#!/usr/bin/env python
# coding: utf-8


# get_ipython().run_line_magic('matplotlib', 'inline')
# get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")

import matplotlib.pyplot as plt

import numpy as np
import torch
import os
from torch import nn
from torch import optim
import torch.nn.functional as F
from torchvision import datasets, transforms, models
from PIL import Image
from torch.autograd import Variable
from binaryClassifier import Net
import csv


'''Update the data_dir to input data location and the model location'''
def generate_typing_results(usage_root_dir):
    usage_name = os.path.basename(os.path.normpath(usage_root_dir))
    image_root_dir = os.path.abspath('sym_' + usage_name) # Update the data path. The images needs
    # to be in a subfolder within the location given here.
    output_filename = os.path.join(image_root_dir, 'typing_result.csv')

    classes = ['typing','noTyping']

    model = Net()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint = torch.load('/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/binaryClassifier/model_cifar.pt') #Update the saved model location
    model.load_state_dict(checkpoint)
    model.eval()

    test_transforms = transforms.Compose([transforms.Resize((224, 224)),
                transforms.ToTensor()]) # need to transform the image with same parameters as training image

    # instantiate the dataset and dataloader
    dataset = ImageFolderWithPaths(image_root_dir, transform=test_transforms)  # our custom dataset
    dataloader = torch.utils.data.DataLoader(dataset)

    # iterate over data
    with open(output_filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        csvheader = ['filename', 'typing_result']
        csvwriter.writerow(csvheader)
        for images, labels, paths in dataloader:
            to_pil = transforms.ToPILImage()
            for i in range(len(images)):
                image = to_pil(images[i])
                index = predict_image(image, test_transforms, device, model)
                # print(paths , ":",str(classes[index]))
                if str(classes[index]) == 'typing':
                    row = [str(paths[0]).replace(image_root_dir + '/', ''), 'typing']
                    csvwriter.writerow(row)



'''Predicts the image label'''
def predict_image(image, test_transforms, device, model):
    image_tensor = test_transforms(image).float()
    image_tensor = image_tensor.unsqueeze_(0)
    input = Variable(image_tensor)
    input = input.to(device)
    output = model(input)
    index = output.data.cpu().numpy().argmax()
    return index


class ImageFolderWithPaths(datasets.ImageFolder):
    """Custom dataset that includes image file paths. Extends
    torchvision.datasets.ImageFolder
    """
    # override the __getitem__ method. this is the method that dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super(ImageFolderWithPaths, self).__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = (original_tuple + (path,))
        return tuple_with_path

