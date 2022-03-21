import os


FINAL_ARTIFACT_ROOT_DIR = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts'

USAGE_REPO_ROOT_DIR = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo'

PATH_TO_WORD2VEC = '/Users/XXX/Documents/Research/FrUITeR/Develop/CraftDroid/code-release/GoogleNews-vectors-negative300.bin'

EVAL_RESULT_PATH = os.path.join(USAGE_REPO_ROOT_DIR, 'code', 'evaluation', 'all_eval_results.csv')


usage_folder_map = {}
usage_folder_map['signin'] = '1-SignIn'
usage_folder_map['signup'] = '2-SignUp'
usage_folder_map['category'] = '3-Category'
usage_folder_map['search'] = '4-Search'
usage_folder_map['terms'] = '5-Terms'
usage_folder_map['account'] = '6-Account'
usage_folder_map['detail'] = '7-Detail'
usage_folder_map['menu'] = '8-Menu'
usage_folder_map['about'] = '9-About'
usage_folder_map['contact'] = '10-Contact'
usage_folder_map['help'] = '11-Help'
usage_folder_map['addcart'] = '12-AddCart'
usage_folder_map['removecart'] = '13-RemoveCart'
usage_folder_map['address'] = '14-Address'
usage_folder_map['filter'] = '15-Filter'
usage_folder_map['addbookmark'] = '16-AddBookmark'
usage_folder_map['removebookmark'] = '17-RemoveBookmark'
usage_folder_map['textsize'] = '18-Textsize'