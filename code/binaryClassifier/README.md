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
