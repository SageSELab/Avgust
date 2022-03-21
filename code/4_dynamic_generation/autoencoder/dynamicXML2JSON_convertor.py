import json
import xmltodict
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
        ifBounds = False
        if type(value) == collections.OrderedDict:
            startX=startY=width=height=endX=endY=0
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
                    elif k == '@text' and v != '':
                        obj['text'] = v
                    elif k == '@width':
                        width = int(v)
                    elif k == '@height':
                        height = int(v)
                    elif k == '@bounds':
                        ifBounds = True
                        first_cor = v.split('][')[0]
                        second_cor = v.split('][')[1]
                        startX = int(first_cor.split(',')[0].replace('[', ''))
                        startY = int(first_cor.split(',')[1])
                        endX = int(second_cor.split(',')[0])
                        endY = int(second_cor.split(',')[1].replace(']', ''))


                elif type(v) == collections.OrderedDict:
                    # print("here1")
                    children.append(get_object({k: v}))
                else:
                    for c in v:
                        children.append(get_object({k: c}))
            if len(children) > 0:
                obj["children"] = children

            if ifBounds == True:
                obj['bounds']  = [startX, startY, endX, endY]
            else:
                obj["bounds"] = [startX, startY, startX+width, startY+height]
        return obj


def convert_to_json_dynamic(input_XML_path):
    try:
        with open(input_XML_path) as xml_file:
            data_dict = dict(xmltodict.parse(xml_file.read()))
        xml_file.close()
        package_name = "Users" # (input_XML_path.split("/")[1]).split("-")[0]
        json_dict = {"activity_name": package_name, "request_id": 3, "is_keyboard_deployed": False}
        # print(json_dict)
        activity = {"added_fragments": ["1"], "active_fragments": ["1"]}
        root = get_object(data_dict)
        root["bounds"] = [0,0,1440,2560]
        activity["root"] = root
        json_dict["activity"] = activity
        output_path = input_XML_path.split(".xml")[0]
        with open(os.path.join(output_path + ".json"), "w") as json_file:
            print('output json file to ', output_path)
            json_file.write(json.dumps(json_dict))
        json_file.close()
    except Exception as e:
        print("error", e)
        pass


if __name__ == '__main__':
    input_XML_path = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models/1-SignIn/dynamic_output/etsy/screenshots/0-0.xml'
    # input_XML_path = '/Users/XXX/Documents/Research/UsageTesting/KNNscreenClassifier/REMAUIOutputNew/about/6pm-about-1/activity_main.xml'
    convert_to_json_dynamic(input_XML_path) # will output the json at the same directory as the xml input
    print('all done! :)')