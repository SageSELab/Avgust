import sys
import os
from xml_to_json_convertor import convert_to_json

count = 0
dir_name = sys.argv[1]

for trace in os.listdir(dir_name):
    if os.path.isdir(os.path.join(dir_name,trace)):
        print("---------trace started------------")
        for screen in os.listdir(os.path.join(dir_name,trace)):
            count = count+1
            print(screen)
            output_path = trace+"_"+screen
            convert_to_json(os.path.join(dir_name,trace,screen), output_path)



print(count)