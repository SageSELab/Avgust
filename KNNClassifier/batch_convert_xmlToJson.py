import sys
import os
from xml_to_json_convertor import convert_to_json, convert_to_json_new_data

count = 0

outputLocationonDevice= '/Users/XXX/Documents/screenClassifier' #change this for your device
# '/Users/XXX/Documents/AutoSeq-Android-Testing/uiClassification'

outputFolder =os.path.join(outputLocationonDevice,'classificationInputAdditional')
os.mkdir(outputFolder)
# inputFolder = sys.argv[1] #give REMAUI output here eg/ 1-SignIn_REMAUI_output
inputs =[]
scriptLocation = os.getcwd()
print(scriptLocation)
#OLD INPUT FOLDERS
# inputs.append('1-SignIn')
# inputs.append('2-SignUp')
# inputs.append('3-Category')
# inputs.append('4-Search')
# inputs.append('5-Terms')
# inputs.append('6-Account')
# inputs.append('7-Detail')
# inputs.append('8-Menu')
# inputs.append('9-About')
# inputs.append('10-Contact')
# inputs.append('11-Help')
# inputs.append('12-AddCart')
# inputs.append('13-RemoveCart')
# inputs.append('14-Address')
# inputs.append('15-Filter')
# inputs.append('16-AddBookmark')
# inputs.append('17-RemoveBookmark')
# inputs.append('18-Textsize')

#NEW INPUT FOLDERS
inputs.append('about')
inputs.append('alert')
inputs.append('checkout')
inputs.append('contact')
inputs.append('help')
inputs.append('pwd_assistant')
inputs.append('signin_amazon')
inputs.append('signin_fb')
inputs.append('signin_google_popup')
inputs.append('state_spinner')



for inputFolder in inputs:
    outputLabelSubFolder = os.path.join(outputFolder,inputFolder)
    os.mkdir(outputLabelSubFolder)

    inputFolderPath = os.path.join(scriptLocation,"REMAUIOutputNew")
    inputFolderPath = os.path.join(inputFolderPath,inputFolder)
    appList = os.listdir(inputFolderPath)
    for app in appList:
        # print(app,"===========APP")
        appPath = os.path.join(inputFolderPath,app)
        outputAppSubFolder= os.path.join(outputLabelSubFolder,app)
        os.mkdir(outputAppSubFolder)
        if '.DS_Store' not in appPath:
            screenList = os.listdir(appPath)
            screenList = [item for item in screenList if item.endswith('.xml')]
            for screen in screenList:
                # print(screen,"=========SCREEN")
                screenPath = os.path.join(appPath,screen)
                output_path= os.path.join(outputAppSubFolder,screen)

                # convert_to_json(screenPath, output_path)
                convert_to_json_new_data(screenPath, output_path)

    # for trace in os.listdir(dir_name):
    #     if os.path.isdir(os.path.join(dir_name,trace)):
    #         print("---------trace started------------")
    #         for screen in os.listdir(os.path.join(dir_name,trace)):
    #             count = count+1
    #             print(screen)
    #             output_path = trace+"_"+screen
    #             convert_to_json(os.path.join(dir_name,trace,screen), output_path)



        # print(count)
