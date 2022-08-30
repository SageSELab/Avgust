**folder structure**

`usage_root_dir` (e.g., `video_data_examples`) contains all artifacts of particular usage (e.g., "Sign In” usage), organized by per video recording. Each sub directory (e.g., `etsy-signin-1`) contains the artifacts related to `etsy-signin-1.mp4` video recording:

- `detected_frames` — all the frames detected from the video recording
- `clicked_frames` — subset of `detected_frames` that only has the frames that contain an action (e.g., click action)
- `steps_clen` — subset of  `clicked_frames` that only contains the relevant actions that will be represented in the SM (e.g., the actions of typing each character on the keyboard are eliminated). If the action is `swipe` or `long_tap`, the respective filename will show such special actions (including swiping direction), e.g., `bbox-X-swipe-up.jpg`, `bbox-Y-long.jpg`. Otherwise, the action is a regular click.
- `ir_data` — contains the same frames as in `steps_clean` **except for swipe actions**, separated by the extracted screen images **without the touch indicator**, and the extracted GUI widgets that the touch indicator refers to
