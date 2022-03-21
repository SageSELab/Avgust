import os, shutil, time

dir_to_script = "C:/Users/XXXy/Documents/label-studio/scripts/serve_local_files_windows.sh"
usage_root_dir = "C:/Users/XXXy/Documents/UsageTesting/video_data_examples/"


json = open("import_data.json", "w+")

new_folder = usage_root_dir+".all_ir_data/"
if not os.path.exists(new_folder):
    os.makedirs(new_folder)


folders = [folder for folder in os.listdir(usage_root_dir) if os.path.isdir(os.path.join(usage_root_dir, folder)) and not folder.startswith('.')]
for i in folders:
    dir_to_ir = usage_root_dir + i + "/ir_data/"

    for image in os.listdir(dir_to_ir):
        shutil.copy(dir_to_ir+image, new_folder+image)
    

os.system(f'start {dir_to_script} {new_folder} *.jpg')

time.sleep(1)

f = open("images.txt", "r")

lines = f.readlines()
json.write("[\n")

temp = ""
for count, i in enumerate(lines):
    i = (i.split("\n"))[0]
    print(i)

    if count%2 == 0:
        temp = i
    else:
        json.write("{\n\t\"data\": {\n\t\"screen\": \""+temp+"\",\n\t\"widget\": \""+i+"\"}\n},\n")


f.close()

os.remove("images.txt")
    

json.write("]")
json.close()
shutil.move("import_data.json", os.path.join(usage_root_dir, "import_data.json"))
