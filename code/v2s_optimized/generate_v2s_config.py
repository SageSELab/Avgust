import json
import os
import copy

sample_config_path = '/mnt/nfs/work1/brun/XXXzhao/video2scenario/config_files/v2s_config_signin.json'
output_config_path = '/mnt/nfs/work1/brun/XXXzhao/video2scenario/config_files/v2s_config_search.json'
video_dir = '/mnt/nfs/scratch1/XXXzhao/input/Search/'

with open(sample_config_path) as f:
  sample_config = json.load(f)

sample_scenario = sample_config['scenarios'][0]
output_scenarios = []
scenario = sample_scenario

for video_file in os.scandir(video_dir):
    if video_file.path.endswith(".mp4") and video_file.is_file():
        scenario['video_path'] = video_file.path # update video path
        filename = os.path.basename(video_file.path)
        scenario['app_name'] = filename.split("-")[0] # update app name
        output_scenarios.append(copy.deepcopy(scenario))

output_config = {}
output_config['scenarios'] = output_scenarios
output_config['packages'] = sample_config['packages']

with open(output_config_path, 'w') as json_file:
  json.dump(output_config, json_file)