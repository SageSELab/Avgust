# phase1.py
import json
import logging
import os
import sys

import numpy as np
from v2s.phase import AbstractPhase
from v2s.phase1.detection.opacity_detection import OpacityDetectorALEXNET
from v2s.phase1.detection.touch_detection import TouchDetectorFRCNN
from v2s.phase1.video_manipulation.video_manipulation import FrameExtractor
from v2s.util.general import JSONFileUtils
from v2s.util.screen import Frame, ScreenTap


class Phase1V2S(AbstractPhase):
    """
    Phase 1 of V2S. Responsible for detecting touches within a recorded video 
    and detecting opacity of touches. 

    Attributes
    ----------
    config : dict
        configuration with video/replay information
    touch_detector : TouchDetectorFRCNN
        touch detector to detect touches in frame
    opacity_detector : OpacityDetectorALEXNET
        opacity detector for touches
    frame_extractor : FrameExtractor
        frame extractor for video
    detections : list of Frames
        output of phase
    
    Methods
    -------
    execute()
        Executes phase. Takes in video and ouputs touch detections with
        opacity confidence.
    add_opacity_to_detections()
        Adds the opacity predictions output by the opacity detector to the frames
        that will be output to a json file.
    get_detections()
        Returns detections of phase 1.
    set_detections(list)
        Changes detections to specified value.
    """
    
    def __init__(self, config):
        """
        Parameters
        ----------
        config : dict
            configuration for video file and device
        """
        self.config = config
        self.frame_extractor = FrameExtractor()
        self.touch_detector = TouchDetectorFRCNN()
        # frames will be set later
        self.opacity_detector = OpacityDetectorALEXNET(None)
        self.detections = []
    
    def execute(self):
        """
        Executes phase. Takes in video and ouputs touch detections with
        opacity confidence.
        """
        cur_path = self.config["video_path"]
        # separate the name and extension of the file
        video_dir, video_file = os.path.split(cur_path)
        video_name, video_extension = os.path.splitext(video_file)
        cur_dir_path = os.path.join(os.path.dirname(cur_path), video_name)

        if not os.path.exists(cur_path):
            sys.exit("ERROR: Specified video does not exist " + cur_path)
        # create output folder where all of the generated files will be stored
        if not os.path.exists(cur_dir_path):
            os.mkdir(cur_dir_path)

        logging.basicConfig(filename=os.path.join(cur_dir_path, 'v2s.log'), filemode='w', level=logging.INFO)
        
        # 1) Execute frame extraction      
        self.frame_extractor.set_video_path(cur_path)
        self.frame_extractor.execute()

        # 2) Execute touch detection, TIME CONSUMING part
        # get the proper model

        ## Read incomplete detections.json; Util/screen.py —> ScreenTap class has all info
        if os.path.exists(os.path.join(cur_dir_path, "incomplete_detections.json")):
            print('incomplete_detections.json exists')
            # convert dict to list of Frames
            incomplete_detections_dict = JSONFileUtils.read_data_from_json(
                os.path.join(cur_dir_path, "incomplete_detections.json"))
            incomplete_detections = []
            for detection_dict in incomplete_detections_dict:
                frame = detection2Frame(detection_dict)
                incomplete_detections.append(frame)
        else:
            print('incomplete_detections.json not found, need to compute and please be patient :)')
            touch_model = os.path.join(sys.prefix, self.config["touch_model"])
            self.touch_detector.set_video_path(cur_path)
            self.touch_detector.set_model_path(touch_model)
            labelmap = os.path.join(sys.prefix, self.config["labelmap"])
            self.touch_detector.set_labelmap_path(labelmap)
            self.touch_detector.execute_detection()
            # incomplete detections - without opacity information
            incomplete_detections = self.touch_detector.get_touch_detections()
            JSONFileUtils.output_data_to_json(incomplete_detections,
                                              os.path.join(cur_dir_path, "incomplete_detections.json"))
        
        # 3) Execute opacity detection
        # get the proper opacity model
        opacity_model = os.path.join(sys.prefix, self.config["opacity_model"])

        self.opacity_detector.set_video_path(cur_path)
        self.opacity_detector.set_model_path(opacity_model)
        self.opacity_detector.set_frames(incomplete_detections)
        # get the touch indicator size
        device_model = self.config["device_model"]
        device_path = os.path.join(sys.prefix, 'v2s', 'device_config.json')
        device_file = open(device_path, 'r') 
        device_specs = json.load(device_file)[device_model]
        touch_indicator = device_specs["indicator_size"]
        self.opacity_detector.set_indicator_size(round(touch_indicator*0.8))
        self.opacity_detector.execute_detection()
        predictions = self.opacity_detector.get_opacity_predictions()
        self.detections = self.add_opacity_to_detections(predictions, 
                                                         incomplete_detections,
                                                         cur_path)

        # 4) Write these detections to json file
        # navigate to file pertaining to video being analyzed
        json_path = os.path.join(cur_dir_path, "detection_full.json")
        JSONFileUtils.output_data_to_json(self.detections, json_path)

    def add_opacity_to_detections(self, predictions, incomplete, cur_vid):
        """
        Adds the opacity predictions output by the opacity detector to the frames
        that will be output to a json file.

        Parameters
        ----------
        predictions : array
            opacity predictions from model
        incomplete : list of Frames
            list of detections lacking opacity information
        cur_path : string
            path to the current video being processed; allows cropped images
            to be found
        
        Returns
        -------
        detections : list of Frames
            detections complete with opacity predictions
        """
        
        # frame id dictionary for detection ids
        # allow to easily match id number from cropped images to correct frame
        frame_ids = {}
        for frame in incomplete:
            frame_ids[frame.get_id()] = frame

        # get path to cropped images
        video_dir, video_file = os.path.split(cur_vid)
        video_name, video_extension = os.path.splitext(video_file)
        cropped_img_path = os.path.join(video_dir, video_name, "cropped_images")

        # get images located at cropped img path
        # sort them so they're in the same order as opacity detection occurred
        img_list = [img for img in os.listdir(cropped_img_path) if 
                                            os.path.splitext(img)[1] == ".jpg"]
        img_list.sort()

        if len(img_list) != np.size(predictions, 0):
            sys.exit("ERROR: Number of predictions does not match number of \
            cropped images. Cannot add opacity predictions to detections.")

        for num, prediction in enumerate(predictions):
            # extract the prediction that the indicator is low opacity
            op_pred = prediction[0].item() #.item() converts from np.float32 to float
            img_name = img_list[num]
            # image name is formatted as "<id>_<tap_num>.jpg"
            # want to get the information about the frame id and the tap number
            split = img_name.split("_")
            frame_id = int(split[0])
            tap_number = int(split[1].split(".")[0])
            # get the frame that we need to add this prediction to
            frame = frame_ids[frame_id]
            tap_list = frame.get_screen_taps()
            # get the tap that this prediction should be added to
            correct_tap = tap_list[tap_number]
            correct_tap.set_opacity_confidence(op_pred)
        
        # detections have now been added to incomplete and can be returned
        return incomplete

    def get_detections(self):
        """
        Returns detections of phase 1.

        Returns
        -------
        detections : dict of string:Frames
            detected frames through touch detection and opacity detection
        """
        return self.detections

    def set_detections(self, dets):
        """
        Changes detections to specified value.

        Parameters
        ----------
        dets : dict of string:Frames
            new detections
        """
        self.detections = dets


def detection2Frame(detection):
    screen_taps_dict = detection['screenTap']
    screen_taps = []
    for screen_tap_dict in screen_taps_dict:
        screen_tap_obj = ScreenTap(screen_tap_dict['x'], screen_tap_dict['y'], screen_tap_dict['confidence'],
                                   screen_tap_dict['confidenceOpacity'], screen_tap_dict['frame'])
        screen_taps.append(screen_tap_obj)
    frame = Frame(detection['screenId'])
    frame.set_screen_taps(screen_taps)
    return frame