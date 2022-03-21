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
        obj["visible_to_user"] = True
        children = []
        if type(value) == collections.OrderedDict:
            b0 = 0
            b1 = 0
            b2 = 0
            b3 = 0
            for k, v in value.items():
                if type(v) != list and type(v) != collections.OrderedDict:
                    if k == "@android:layout_marginLeft":
                        if v != "match_parent":
                            b0 = int(v[:-2])
                    elif k == "@android:layout_marginTop":
                        if v != "match_parent":
                            b1 = int(v[:-2])
                    elif k == "@android:layout_width":
                        if v != "match_parent":
                            b2 = int(v[:-2])
                    elif k == "@android:layout_height":
                        if v != "match_parent":
                            b3 = int(v[:-2])
                    elif k == "@android:text":
                        obj["text"] = v

                elif type(v) == collections.OrderedDict:
                    print("here1")
                    children.append(get_object({k: v}))
                else:
                    for c in v:
                        children.append(get_object({k: c}))
            if len(children) > 0:
                obj["children"] = children
            obj["bounds"] = [b0, b1, b2, b3]
        return obj


def convert_to_json(path,output_path):
    try:
        with open(os.path.join(path,"activity_main.xml")) as xml_file:
            data_dict = dict(xmltodict.parse(xml_file.read()))
        xml_file.close()
        package_name = (path.split("/")[1]).split("-")[0]
        json_dict = {"activity_name": package_name, "request_id": 3, "is_keyboard_deployed": False}
        activity = {"added_fragments": ["1"], "active_fragments": ["1"]}
        root = get_object(data_dict)
        activity["root"] = root
        json_dict["activity"] = activity

        with open(os.path.join("outputs",output_path+".json"), "w") as json_file:
            json_file.write(json.dumps(json_dict))
        json_file.close()
    except:
        print("error")
        pass
