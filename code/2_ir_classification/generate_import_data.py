import json
import os
import glob

image_root_dir = 'sym_video_data_examples' # change this to the symlink you created
server_addr = 'http://localhost:8081' # change this to your IP address and port used when uploading images

output_json = (image_root_dir.replace('sym', 'import')) + '.json'
tasks = []

for screen_image in glob.glob(image_root_dir + '/*-screen.jpg'):
    new_task = {}
    new_data = {}
    screen_url = screen_image.replace(image_root_dir, server_addr)
    widget_url = screen_url.replace('screen', 'widget')
    new_data['screen'] = screen_url
    new_data['widget'] = widget_url
    new_task['data'] = new_data
    tasks.append(new_task)

with open(output_json, 'w') as f:
    json.dump(tasks, f)

print('all done! :)')