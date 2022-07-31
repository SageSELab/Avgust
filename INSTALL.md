## Setting Up Repo for Test Generation
1. Clone the repository.
2. Install Conda environment for the project using this [environment file for Mac]() or [environment file for Windows](). you can use `conda env create -f environment.yml` to create the environment and activate the environment by `conda activate usage`.
3. install [Appium](http://appium.io/) Desktop
4. add app's configuration in [App_Config.py]() -- you can find relevant info in [news_app_info.csv]() and [shopping_app_info.csv]()
5. start Android Emulator -- make sure the AUT (App Under Test) is installed on the Emulator, e.g., abcnews.
6. start Appium Server on Appium desktop (you do not need to change the default port).
7. Change file paths in [global_config.py](). Final-Artifact can be downloaded [here](https://zenodo.org/record/5940759).
8. run main method in [dynamic_evaluation.py]()

At this point you should be able to see an output similar to the output below on your command line interface:

>>The screen classifier top1 guess for the screen:
category
The screen classifier top5 guesses for the screen:
['category', 'home', 'items', 'menu', 'popup']
Choose the closest screen tag from the top5 guesses: [`You should type the closest screen tag on your cli`]
`home`
---------
>>id:0 floating_search_view - matched with: to_search
id:1 rl_search_box - matched with: to_search
id:2 navigation_home - matched with: home
id:3 navigation_feed - matched with: menu
Choose the id of the widget you want to interact with:[`You should type the id on your cli`]: `0`
Please enter the ground truth IR for the widget you chose:to_search
executing event: resource-id floating_search_view click 

## Running for a usage
1. `usage_root_dir` should point to V2S's results of a usage, e.g., "Combined/SignIn/".
2. run `1_step_extraction/step_extraction.py` to generate `clicked_frames` folder
3. go to `binaryClassifier` and follow the instructions on the next section to generate final `typing_result.csv`.
4. run `1_step_extraction/step_cleaning.py` to generate `steps_clean` folder.
5. run `1_step_extraction/special_step_recognition.py` to append special actions in `steps_clean` folder.
6. run `2_ir_classification/screen_widget_extraction.py` to generate `ir_data_auto` folder with screens only.
7. get UIED results (run UIED v2.3's `run_mybatch.py`) -- check terminal for running time as this process is time-consuming.
8. run `2_ir_classification/screen_widget_extraction.py` to add widget crops to `ir_data_auto` folder.

### Instructions for running binaryClassifier
binary classifier classifies whether an image contains keyboard typing or not
- `binaryClassifier.py` trains a classifier based on the data specified under `/data/` folder
- `labelPredictor.py` uses the trained classifier (output of `binaryClassifier.py`) to predict whether an image has keyboard typing or not
- `cropImage.py` crops keyboard part (bottom part) of the entire screenshot for better accuracy
- `typingLocator.py` adds the results of whether the touch indicator is on the keyboard (`in`) or not (`out`) to the `typing_result.csv` file

To use the pre-trained classifier:
1. run `crop_clicked_frames.py` to generate `clicked_frames_crop` folder
2. run `create_symlink.py` to create symlinks (will be under `binaryClassifier` folder
3. run `labelPredictor.py` to generate `typing_result.csv` under the symlink folder
4. run `typingLocator.py` to update `typing_result.csv` under the symlink folder (this is the final `typing_result.csv`)

## Running UIED v2.3
1. `ImportError: No module named 'detect_text_east.lib_east.lanms.adaptor’` — check this [thread](https://github.com/argman/EAST/issues/174). Replace the Makefile in `/detect_text_east/lib_east/lanms` and go to that directory to run `make` command.
