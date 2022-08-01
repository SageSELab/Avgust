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
