import json, os

# recognize long_tap and swipes (including its direction)
# and rename the bbox-xxx file

### input parameters you need to change ###
usage_root_dir = os.path.abspath("/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/11-Help") # directory to v2s data of a particular usage
### end of input parameters ###


def add_special_action(usage_root_dir):
    dir_to_rename = "steps_clean"  # will rename the files in this folder to add special cases, such as swipe direction
    for folder in os.listdir(usage_root_dir):
        if os.path.isdir(os.path.join(usage_root_dir, folder)):
            dir_to_json = os.path.join(usage_root_dir, folder, "detected_actions.json")
            dir_to_steps_clean = os.path.join(usage_root_dir, folder, dir_to_rename)

            print("\nStarting " + folder)
            file = open(dir_to_json, )
            data = json.load(file)

            for j in range(len(data)):
                act_type = data[j]['act_type']
                if act_type == "LONG_CLICK":
                    frames = data[j]['frames']

                    for i in frames:
                        if len(str(i)) == 1:
                            img = "bbox-000" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-long.jpg"))
                                print("renamed " + img + " to long")
                            except:
                                pass
                        elif len(str(i)) == 2:
                            img = "bbox-00" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-long.jpg"))
                                print("renamed " + img + " to long")
                            except:
                                pass
                        elif len(str(i)) == 3:
                            img = "bbox-0" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-long.jpg"))
                                print("renamed " + img + " to long")
                            except:
                                pass
                        elif len(str(i)) == 4:
                            img = "bbox-" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-long.jpg"))
                                print("renamed " + img + " to long")
                            except:
                                pass


                elif act_type == "SWIPE":
                    # print(data[j]['frames'])
                    frames = data[j]['frames']
                    swipe = ""

                    x_1 = data[j]["taps"][0]['x']
                    y_1 = data[j]["taps"][0]['y']

                    x_2 = data[j]["taps"][len(frames) - 1]['x']
                    y_2 = data[j]["taps"][len(frames) - 1]['y']

                    if abs(x_1 - x_2) > abs(y_1 - y_2):
                        if x_2 > x_1:
                            swipe = "right"
                        else:
                            swipe = "left"
                    else:
                        if y_2 > y_1:
                            swipe = "down"
                        else:
                            swipe = "up"
                    # print(swipe)
                    for i in frames:
                        if len(str(i)) == 1:
                            img = "bbox-000" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-swipe-" + swipe + ".jpg"))
                                print("renamed " + img + " to " + swipe)
                            except:
                                pass
                        elif len(str(i)) == 2:
                            img = "bbox-00" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-swipe-" + swipe + ".jpg"))
                                print("renamed " + img + " to " + swipe)
                            except:
                                pass
                        elif len(str(i)) == 3:
                            img = "bbox-0" + str(i)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-swipe-" + swipe + ".jpg"))
                                print("renamed " + img + " to " + swipe)
                            except:
                                pass
                        elif len(str(i)) == 4:
                            img = "bbox-" + str(i)
                            print(img)
                            try:
                                os.rename(os.path.join(dir_to_steps_clean, img + '.jpg'),
                                          os.path.join(dir_to_steps_clean, img + "-swipe-" + swipe + ".jpg"))
                                print("renamed " + img + " to " + swipe)
                            except:
                                pass

            print("Finished " + folder)
            file.close()
