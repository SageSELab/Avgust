import json
import xmltodict
import sys
import collections
import os

# package_name = sys.argv[1]

def get_object(data_dict):
    obj = {}
    for key, value in data_dict.items():
        obj["class"] = key
        if 'Layout' in key:
            obj["visibility"]= ""
        else:
            obj["visibility"]= "visible"
        children = []
        if type(value) == collections.OrderedDict:
            startX=startY=width=height=0

            for k, v in value.items():
                if type(v) != list and type(v) != collections.OrderedDict:
                    if k == "@android:layout_marginLeft":
                        if v != "match_parent":
                            startX = int(v[:-2])
                    elif k == "@android:layout_marginTop":
                        if v != "match_parent":
                            startY = int(v[:-2])
                    elif k == "@android:layout_width":
                        if v != "match_parent":
                            width = int(v[:-2])
                    elif k == "@android:layout_height":
                        if v != "match_parent":
                            height = int(v[:-2])
                    elif k == "@android:text":
                        obj["text"] = v

                elif type(v) == collections.OrderedDict:
                    # print("here1")
                    children.append(get_object({k: v}))
                else:
                    for c in v:
                        children.append(get_object({k: c}))
            if len(children) > 0:
                obj["children"] = children
            obj["bounds"] = [startX, startY, startX+width, startY+height]
        return obj


def convert_to_json_new_data(path,output_path):
    try:
        with open(path) as xml_file:
            data_dict = dict(xmltodict.parse(xml_file.read()))
        xml_file.close()
        package_name = (path.split("/")[1]).split("-")[0]
        json_dict = {"activity_name": package_name, "request_id": 3, "is_keyboard_deployed": False}
        activity = {"added_fragments": ["1"], "active_fragments": ["1"]}
        root = get_object(data_dict)
        root["bounds"] =  [0,0,1440,2560]
        activity["root"] = root
        json_dict["activity"] = activity
        output_path = output_path.split(".xml")[0]
        with open(os.path.join(output_path+".json"), "w") as json_file:
            json_file.write(json.dumps(json_dict))
        json_file.close()
    except Exception as e:
        print("error",e)
        pass
def convert_to_json(path,output_path):
    try:
        with open(os.path.join(path,"activity_main.xml")) as xml_file:
            data_dict = dict(xmltodict.parse(xml_file.read()))
        xml_file.close()
        package_name = (path.split("/")[1]).split("-")[0]
        json_dict = {"activity_name": package_name, "request_id": 3, "is_keyboard_deployed": False}
        activity = {"added_fragments": ["1"], "active_fragments": ["1"]}
        root = get_object(data_dict)
        root["bounds"] =  [0,0,1440,2560]
        activity["root"] = root
        json_dict["activity"] = activity

        with open(os.path.join(output_path+".json"), "w") as json_file:
            json_file.write(json.dumps(json_dict))
        json_file.close()
    except Exception as e:
        print("error",e)
        pass
