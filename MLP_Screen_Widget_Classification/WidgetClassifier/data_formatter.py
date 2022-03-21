import os
import json
from PIL import Image


def get_text_ocr(image_path):
    ocrResult = pytesseract.image_to_string(image_path)
    proc_ocr_text = ocrResult.replace('\r', '').replace('\n', '').replace('\"', '\'').replace('<', '').replace('>', '')
    result = proc_ocr_text.replace('\x00', '').replace('\x08', '').replace('\x0c', '')
    result = result.lower()
    return result


import pytesseract

input_path = "redrawResult"
artifact_path = "UsageTesting-Artifacts"
widget_class_dict = {}
widget_text_dict = {}


def format_widget_class_data():
    for class_list_file in os.listdir("redrawResult"):
        if class_list_file != ".DS_STORE":
            # print(class_list_file)
            file = open(os.path.join(input_path, class_list_file))
            data = json.load(file)
            widget_class_dict.update(data)

    print(widget_class_dict)


def extract_text_data_from_widget():
    counter = 0
    for usage in os.listdir(artifact_path):
        if usage != ".DS_STORE" and os.path.isdir(os.path.join(artifact_path, usage)):
            for scenario in os.listdir(os.path.join(artifact_path, usage)):
                if scenario != ".DS_STORE" and os.path.isdir(os.path.join(artifact_path, usage, scenario)):
                    for file in os.listdir(os.path.join(artifact_path, usage, scenario, "ir_data_auto")):
                        if "widget" in file:
                            text = get_text_ocr(os.path.join(artifact_path, usage, scenario, "ir_data_auto", file))
                            widget_text_dict[file] = text
                            counter = counter + 1
                            print(counter)


def clean_widget_text_file():
    file = open("widget_text.json")
    data = json.load(file)
    for key, value in data.items():
        value = value.replace('\u00a9', '').replace('\u2018', '').replace('\u2019', '').replace('\u00a5', '').replace(
            '\u2014', '').replace('\u2019', '').replace('\u00a5', '').replace('\u00ab', '').replace('\u20ac', '').replace('\u00b0', '').replace('\u00ae', '').replace('\u201c', '').replace('\u00b0', '').replace('\u00bb', '').replace('\u2122', '').replace('\u00a7', '').replace('\u00a2', '').replace('\u00e9', '').replace('\u00a2', '')

        clean_widget_text_dict[key] = value


# extract_text_data_from_widget()
# print(widget_text_dict)
#
# with open('widget_text.json', 'w') as result_file:
#     result_file.write(json.dumps(widget_text_dict))

# clean_widget_text_dict = {}
# clean_widget_text_file()
# with open('widget_text_clean.json', 'w') as result_file:
#     result_file.write(json.dumps(clean_widget_text_dict))

format_widget_class_data()
widget_text_file = open("widget_text_clean.json")
widget_text_dict = json.load(widget_text_file)

final_widget_data = {}
for key,value in widget_text_dict.items():
    final_widget_data[key] = [value, widget_class_dict[key]]

# print(final_widget_data)
with open('widget_data.json', 'w') as result_file:
    result_file.write(json.dumps(final_widget_data))

