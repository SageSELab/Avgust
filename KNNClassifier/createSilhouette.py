#!/usr/bin/env python
# coding: utf-8

# In[28]:


import json
import math
from PIL import Image, ImageDraw
import os
import sys
from time import sleep
# #filepath="an.SpanishTranslate\\trace_0\\view_hierarchies\\107.json"
# filepath="afzkl.development.mVideoPlayer\\trace_0\\view_hierarchies\\2606.json"
# filtered_traces_path="..\\..\\2021-1-Spring\\Kevin_Moran_CS697\\rico_dataset\\filtered_traces\\"
resolution=[1440,2560]
resized_resolution=(int(resolution[0]/10),int(resolution[1]/10))


# In[29]:


def printLoading(numOfImg,totalNumOfScreens):
    message="Images saved "+str(numOfImg)+"/"+str(totalNumOfScreens)
    sys.stdout.write('\r')
    sys.stdout.write(message)
    sys.stdout.flush()
    sleep(0.0001)


# In[30]:


def getData(data,attribute):
    blank=""
    try:
        attrData=data.get(attribute)
        if attrData==None:
            return blank
        else:
            return attrData
    except(AttributeError):
        return blank





# In[31]:


def findTextualUI(data,textObjs,nonTextObjs):

    if(getData(data,"children")!=""):
        #print("got children")
        children=getData(data,"children")
        for child in children:
            findTextualUI(child,textObjs,nonTextObjs)
    else:
        text=getData(data,"text")
        if getData(data,"visibility")=='visible': #changed from visibility to visible_to_user, visible to true
            if text!="":
                clazz=getData(data,"class")
                clazz=clazz.lower()
                #print(clazz)
                if "edittext" not in clazz:
                    #textUI=(text,data.get("bounds"))
                    #print("Text object:",end="\t")
                    #print(text,end="\t")
                    bound=getData(data,"bounds")
                    #print(bound)
                    textObjs.append(bound)
                    #print(text,end="\t")
                    #print(data.get("bounds"))
            else:
                #print("Non-Text object:",end="\t")
                #print(text,end="\t")
                bound=getData(data,"bounds")
                #print(bound)
                nonTextObjs.append(bound)




# In[32]:


def createUIImage(uiFilePath,outPath,app):
    try:
        with open(uiFilePath) as json_data:
            data = json.load(json_data)
    except:
        print(uiFilePath)
    #print(uiFilePath)
    ui = uiFilePath.split("/")[-1].split(".")[0] #fileName
    data=getData(data,"activity")
    data=getData(data,"root")
    textObjs=[]
    nonTextObjs=[]
    findTextualUI(data,textObjs,nonTextObjs)

    tShapes=[]
    ntShapes=[]

    for bound in textObjs:
        tShapes.append([(bound[0],bound[1]),(bound[2],bound[3])])
    for bound in nonTextObjs:

        ntShapes.append([(bound[0],bound[1]),(bound[2],bound[3])])
    # creating new Image object
    img = Image.new("RGB", (resolution[0], resolution[1]))
    # create rectangle images
    for shape in tShapes:
        textObj=ImageDraw.Draw(img)
        #Text object will be drawn in yellow
        textObj.rectangle(shape, fill ="#ffff33", outline ="yellow",width=10)
    for shape in ntShapes:
        #Non text object will be drawn in blue
        nontextobj=ImageDraw.Draw(img)
        nontextobj.rectangle(shape, fill ="#339FFF", outline ="blue", width=10)
    img=img.resize(resized_resolution)
    #save image
    outputPath = os.path.join(outPath,app+"-"+ui+".jpg")
    img.save(outputPath)



# In[33]:


# apps=os.listdir(filtered_traces_path)
# appTraceList=[]
currentDir = os.getcwd()
outputFolder = os.path.join(currentDir,'outputLayoutImage')
os.mkdir(outputFolder)

inputFolder = os.path.join(currentDir,'classificationInput')
labelCategories = os.listdir(inputFolder)
# labelCategories =['SignIn-Screen2Vec-JSON-input']

separateByLabelAndApp = False
if not separateByLabelAndApp:
    outputLocation = outputFolder
# print(outputFolder)
for labelCategory in labelCategories:
    labelInputPath = os.path.join(inputFolder,labelCategory)
    if separateByLabelAndApp:
        labelOutputPath = os.path.join(outputFolder,labelCategory)
        os.mkdir(labelOutputPath)


    appList = os.listdir(labelInputPath)
    for app in appList:
        appInputPath = os.path.join(labelInputPath,app)
        if separateByLabelAndApp:
            appOutputPath = os.path.join(labelOutputPath,app)
            os.mkdir(appOutputPath)
            outputLocation = appOutputPath

        jsonFileList = os.listdir(appInputPath)


        totalNumOfScreens = len(jsonFileList)
        for num, jsonFile in enumerate(jsonFileList):
            if '.json' in jsonFile:
                jsonPath = os.path.join(appInputPath,jsonFile)
                # print(jsonPath,outputLocation)
                createUIImage(jsonPath,outputLocation,app)
                printLoading(num,totalNumOfScreens)
        # break
