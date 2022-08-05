## Setting Up Repo for Test Generation
1. Clone the repository.
2. Install Conda environment for the project using this [environment file for Mac](https://github.com/SageSELab/Avgust/blob/main/REQUIREMENTS-mac.txt) or [environment file for Windows](https://github.com/SageSELab/Avgust/blob/main/REQUIREMENTS-windows.txt). you can use `conda env create -f environment.yml` to create the environment and activate the environment by `conda activate usage`.
3. install [Appium](http://appium.io/) Desktop
4. add app's configuration in [App_Config.py](https://github.com/SageSELab/Avgust/blob/main/code/4_dynamic_generation/App_Config.py) -- you can find relevant info in [news_app_info.csv](https://github.com/SageSELab/Avgust/blob/main/news_app_info.csv) and [shopping_app_info.csv](https://github.com/SageSELab/Avgust/blob/main/shopping_app_info.csv)
5. start Android Emulator -- make sure the AUT (App Under Test) is installed on the Emulator, e.g., abcnews.
6. start Appium Server on Appium desktop (you do not need to change the default port).
7. Change file paths in [global_config.py](https://github.com/SageSELab/Avgust/blob/main/code/global_config.py). Final-Artifact can be downloaded [here](https://zenodo.org/record/5940759).
8. run main method in [dynamic_evaluation.py](https://github.com/SageSELab/Avgust/blob/main/code/evaluation/dynamic_evaluation.py)

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


**Enabling REMAUI feature**
1. download [REMAUI Java program](https://drive.google.com/file/d/1787v_UKwc06yVC7XA8fh47e98PC9CPTv/view?usp=sharing)
2. install [Eclipse](https://www.eclipse.org/) for Java if you don't already have it
3. use Eclipse to import the REMAUI Java program
4. configure all the build paths (the REMAUI repo should already contain all the necessary jars except for openCV) -- see screenshots below regarding build path. you need to edit the paths of jar files to the file paths on your machine

<img width="689" alt="image" src="https://user-images.githubusercontent.com/5572614/155231533-66c8ec47-a101-4396-bfe7-95e4518b333d.png">
<img width="1007" alt="image" src="https://user-images.githubusercontent.com/5572614/155231617-2f6c6b5d-20f4-4ce2-920a-dbb5d2a20d6e.png">


4. follow this [tutorial](https://docs.opencv.org/2.4/doc/tutorials/introduction/java_eclipse/java_eclipse.html) to enable openCV (see notes below first if using Mac)
5. double check the main method in `edu.wm.cs.semeru.redraw.REMAUI`, it should only have `run_REMAUI_single_image(args[0]);`.
6. run the main method in `edu.wm.cs.semeru.redraw.REMAUI` through Eclipse's "run configurations" and give one argument which is the path of a screen image (see below). (Make sure to change file path in `run_REMAUI_single_image` function, including `projectRootDirectory`, and `screenshots` String which should be the folder name that contains the image). REMAUI output should be in the parent folder of the image path. 
7. After running sccessfully, copy the command and replace `REMAUI_cmd` in [state.py](https://github.com/SageSELab/Avgust/blob/main/code/4_dynamic_generation/state.py)

If you're using Mac, you need to build openCV yourself in order to have that "build" folder. follow steps below:
1. after downloading openCV's source, make a `build` directory in it. 
2. then you build opencv using cmake command. If you are in the build folder you just created, `cmake ..` will do. Then run `make -j8`
3. from the tutorial above, you should put `build/lib` as the native library location

<img width="979" alt="image" src="https://user-images.githubusercontent.com/5572614/155193946-3e197870-2ebc-46ba-b1c1-b5942fe49b3e.png">

## Running for a usage
1. `usage_root_dir` should point to V2S's results of a usage, e.g., "Combined/SignIn/".
2. run `1_step_extraction/step_extraction.py` to generate `clicked_frames` folder
3. go to `binaryClassifier` and follow the instructions on the next section to generate final `typing_result.csv`.
4. run `1_step_extraction/step_cleaning.py` to generate `steps_clean` folder.
5. run `1_step_extraction/special_step_recognition.py` to append special actions in `steps_clean` folder.
6. run `2_ir_classification/screen_widget_extraction.py` to generate `ir_data_auto` folder with screens only.
7. get UIED results (run UIED v2.3's `run_mybatch.py`) -- check terminal for running time as this process is time-consuming.
8. run `2_ir_classification/screen_widget_extraction.py` to add widget crops to `ir_data_auto` folder.
