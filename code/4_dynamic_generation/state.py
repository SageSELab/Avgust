import sys, os
import pickle

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder', 'aeSrc'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder_KNN'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder_MLP'))
sys.path.insert(0, os.path.join(current_dir_path, 'screen_classifier'))
sys.path.insert(0, os.path.join(current_dir_path, 'widget_classifier'))

import PIL, psutil
import pandas as pd
import torch
import cv2
import json
import pytesseract
from dynamicXML2JSON_convertor import convert_to_json_dynamic
from REMAUI_XML2JSON_convertor import convert_to_json_REMAUI
from createSilhouette import createUIImage
from getEmbeddings import getAEembeddings
from screen_classifier_KNN_autoencoder import KNN_screen_classifier
from MLP_classify import MLP_ScreenClassifierForAUT
from model import ScreenClassifier
from models import UIEmbedder
import classifier_utils


def OCR(path, words_only=True):
    image = cv2.imread(path)
    image = cv2.medianBlur(image, 3)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(PIL.Image.fromarray(image))
    text = text.split()
    return [word.lower() for word in text]

def process_text_data(raw_data, words):
    remove_none_english = [w for w in raw_data if w in words]
    sentence = " ".join(remove_none_english)
    return sentence

class State:
    def __init__(self, screenshot):
        self.screenshot = screenshot
        self.nodes = []
        self.actions = {}
        self.name_actions = {}
        self.activity = ''
        self.transitions = {}
        self.screenshot_path = ''
        self.UIXML_path = ''

    def add_screenshot_path(self, path):
        self.screenshot_path = path

    def add_UIXML_path(self, path):
        self.UIXML_path = path

    def add_node(self, node):
        self.nodes.append(node)

    def get_node(self, node_id):
        return self.nodes[node_id]

    def get_actions(self):
        return self.actions

    def get_name_actions(self):
        return self.name_actions

    def add_action(self, node_id, tag, action_type):
        self.actions[node_id]=action_type
        self.name_actions[tag]=action_type

    def set_activity(self, activity_name):
        self.activity = activity_name

    def add_transition(self, action, state):
        self.transitions[action] = state

    def print_state(self):
        print('Activity:', self.activity)
        print('Actions:', self.name_actions)
        print("-------------------")
        for node in self.nodes:
            if node.interactable:
                print(node.get_exec_identifiers())
        print("-------------------")

    def get_dynamic_embedding(self):
        convert_to_json_dynamic(self.UIXML_path)  # will output the json at the same directory as the xml input
        createUIImage(self.UIXML_path.replace('xml', 'json'))
        dynamic_embedding = getAEembeddings(os.path.dirname(self.UIXML_path), self.UIXML_path.replace('.xml', '-layout.jpg'))
        embedding_path = self.UIXML_path.replace('.xml', '-dynamicEmbedding.pickle')
        with open(embedding_path, 'wb') as file:
            pickle.dump(dynamic_embedding, file)
        return dynamic_embedding

    def get_ocr_text_embedding(self, bert, words):
        text = OCR(self.screenshot_path)
        processed_ocr_text = process_text_data(text, words)
        text_embedding = torch.as_tensor(bert.encode(processed_ocr_text),
                                         device='cpu').reshape(1,
                                                                768)
        return text_embedding

    def get_screen_tag(self, screen_id):
        screen_dict_path = "../4_dynamic_generation/screen_classifier/screen_dict.json"
        with open(screen_dict_path) as screen_dict_file:
            screen_dict = json.load(screen_dict_file)
            for k,v in screen_dict.items():
                if v == screen_id:
                    return k

    def get_REMAUI_embedding(self):
        # call Java program REMAUI to reverse engineering the UI first (you need to find out your Java command line to run the REMAUI program and replace REMAUI_command)
        image_file_to_REMAUI = self.UIXML_path.replace('xml', 'png')
        # REMAUI_cmd = '/Library/Java/JavaVirtualMachines/adoptopenjdk-16.jdk/Contents/Home/bin/java ' \
        #              '-Djava.library.path=/Users/XXX/Documents/dev/opencv-4.5.2/build/lib ' \
        #              '-Dfile.encoding=UTF-8 ' \
        #              '-p /Users/XXX/Documents/dev/REMAUI/javax.persistence-2.2.0.jar ' \
        #              '-classpath /Users/XXX/Documents/dev/REMAUI/bin:/Users/XXX/Documents/dev/opencv-4.5.2/build/bin/opencv-452.jar:/Users/XXX/Documents/dev/REMAUI/lib/jdom/xercesImpl.jar:/Users/XXX/Documents/dev/REMAUI/lib/guava-19.0.jar:/Users/XXX/Documents/dev/REMAUI/lib/ij.jar:/Users/XXX/Documents/dev/REMAUI/lib/gson-2.8.0.jar:/Users/XXX/Documents/dev/REMAUI/Android-Core-1.0.jar:/Users/XXX/Documents/dev/REMAUI/SEMERU-Core-1.0.jar:/Users/XXX/Documents/dev/REMAUI/commons-exec-1.3.jar:/Users/XXX/Documents/dev/REMAUI/commons-lang-2.6.jar:/Users/XXX/Documents/dev/REMAUI/lib/commons-io-2.5.jar:/Users/XXX/Documents/dev/REMAUI/lib/jsoup-1.9.2.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/android-stubs-src.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/javacpp-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/artoolkitplus-2.3.1-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-android-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-android-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/protobuf-java-2.6.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-calibration-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-calibration-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-feature-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-feature-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-geo-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-geo-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-io-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-io-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-ip-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-ip-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-javacv-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-javacv-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-jcodec-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-jcodec-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-learning-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-learning-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-recognition-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-recognition-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-sfm-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-sfm-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-visualize-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-visualize-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-WebcamCapture-0.26-sources.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/BoofCV-WebcamCapture-0.26.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/bridj-0.7.0.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/commons-compress-1.7.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/core-0.30.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/ddogleg-0.10.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/dense64-0.30.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/equation-0.30.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-linux-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-macosx-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-windows-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/opencv-3.0.0-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/flandmark-1.07-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/flycapture-2.8.3.1-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/georegression-0.12.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/io-0.3.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/jarchivelib-0.5.0.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/libdc1394-2.2.3-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/libfreenect-0.5.3-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/videoinput-0.200-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/javacv-1.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/jcodec-0.1.9.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/learning-0.3.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/main-0.3.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/models-0.3.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/opencv-3.0.0-1.1-linux-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/opencv-3.0.0-1.1-macosx-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/opencv-3.0.0-1.1-windows-x86_64.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/simple-0.30.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/slf4j-api-1.7.2.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/snakeyaml-1.17.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/uiautomator.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/webcam-capture-0.3.11.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/xmlpull-1.1.3.1.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/xpp3_min-1.1.4c.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/xstream-1.4.7.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/xz-1.4.jar:/Users/XXX/Documents/dev/REMAUI/lib/boofcv/zip4j-1.3.2.jar:/Users/XXX/Documents/dev/REMAUI/lib/jdom/jdom-2.0.6.jar edu.wm.cs.semeru.redraw.REMAUI ' \
        #              + image_file_to_REMAUI
        REMAUI_cmd = '/Library/Java/JavaVirtualMachines/openjdk-13.0.1.jdk/Contents/Home/bin/java ' \
                     '-Djava.library.path=/Users/XXX/Documents/Research/UsageTesting/opencv-4.5.2/build/lib:/Users/XXX/Documents/Research/UsageTesting/opencv-4.5.2/build/lib ' \
                     '-Dfile.encoding=UTF-8 ' \
                     '-p /Users/XXX/Documents/Research/UsageTesting/REMAUI/javax.persistence-2.2.0.jar ' \
                     '-classpath /Users/XXX/Documents/Research/UsageTesting/REMAUI/bin:/Users/XXX/Documents/Research/UsageTesting/opencv-4.5.2/build/bin/opencv-452.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/jdom/xercesImpl.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/guava-19.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/ij.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/gson-2.8.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/Android-Core-1.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/SEMERU-Core-1.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/commons-exec-1.3.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/commons-lang-2.6.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/commons-io-2.5.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/jsoup-1.9.2.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/android-stubs-src.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/javacpp-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/artoolkitplus-2.3.1-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-android-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-android-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/protobuf-java-2.6.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-calibration-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-calibration-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-feature-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-feature-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-geo-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-geo-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-io-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-io-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-ip-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-ip-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-javacv-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-javacv-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-jcodec-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-jcodec-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-learning-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-learning-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-recognition-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-recognition-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-sfm-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-sfm-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-visualize-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-visualize-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-WebcamCapture-0.26-sources.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/BoofCV-WebcamCapture-0.26.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/bridj-0.7.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/commons-compress-1.7.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/core-0.30.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/ddogleg-0.10.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/dense64-0.30.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/equation-0.30.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-linux-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-macosx-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1-windows-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/ffmpeg-2.8.1-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/opencv-3.0.0-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/flandmark-1.07-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/flycapture-2.8.3.1-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/georegression-0.12.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/io-0.3.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/jarchivelib-0.5.0.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/libdc1394-2.2.3-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/libfreenect-0.5.3-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/videoinput-0.200-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/javacv-1.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/jcodec-0.1.9.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/learning-0.3.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/main-0.3.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/models-0.3.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/opencv-3.0.0-1.1-linux-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/opencv-3.0.0-1.1-macosx-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/opencv-3.0.0-1.1-windows-x86_64.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/simple-0.30.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/slf4j-api-1.7.2.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/snakeyaml-1.17.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/uiautomator.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/webcam-capture-0.3.11.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/xmlpull-1.1.3.1.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/xpp3_min-1.1.4c.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/xstream-1.4.7.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/xz-1.4.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/boofcv/zip4j-1.3.2.jar:/Users/XXX/Documents/Research/UsageTesting/REMAUI/lib/jdom/jdom-2.0.6.jar edu.wm.cs.semeru.redraw.REMAUI ' \
                     + image_file_to_REMAUI
        os.system(REMAUI_cmd)
        XML_basename = os.path.basename(os.path.normpath(self.UIXML_path)).replace('.xml', '')
        REMAUI_XML_path = os.path.join(os.path.dirname(self.UIXML_path), '..', 'REMAUI', XML_basename, 'activity_main.xml')
        REMAUI_error = convert_to_json_REMAUI(REMAUI_XML_path)  # will output the json at the same directory as the xml input
        while REMAUI_error is not None:
            print('REMAUI error:', REMAUI_error)
            input('please fix the XML and continue')
            REMAUI_error = convert_to_json_REMAUI(REMAUI_XML_path)

        createUIImage(REMAUI_XML_path.replace('xml', 'json'))
        REMAUI_embedding =  getAEembeddings(os.path.dirname(REMAUI_XML_path), REMAUI_XML_path.replace('.xml', '-layout.jpg'))
        embedding_path = REMAUI_XML_path.replace('.xml', '-REMAUIEmbedding.pickle')
        with open(embedding_path, 'wb') as file:
            pickle.dump(REMAUI_embedding, file)
        return REMAUI_embedding

    def explore_screen_classifiers(self, dynamicXML_embedding_autoencoder, REMAUI_embedding_autoencoder,
                                   AUT, usage_model, text_sim_w2v, text_sim_bert, REMAUI_flag, true_IR=None):

        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        embeddings_path = os.path.join(current_dir_path, "autoencoder_KNN", "autoencoder_embeddings")
        K = 5
        N = 5
        labels_path = [os.path.join(current_dir_path, "autoencoder_KNN/final_labels_all.csv"),
                       os.path.join(current_dir_path, "autoencoder_KNN/augmented_labels.csv")]
        screen_classifier_KNN = KNN_screen_classifier(AUT, embeddings_path, labels_path, K, N)
        screen_classifier_MLP = MLP_ScreenClassifierForAUT(autoencoder=True)

        # Find Screen title (top-left corner)
        screenIR_KNN, top_n_screenIR_KNN = screen_classifier_KNN.run_knn_query(dynamicXML_embedding_autoencoder)
        screenIR_MLP, top_n_screenIR_MLP = screen_classifier_MLP.classify(dynamicXML_embedding_autoencoder, AUT, N)

        KNN_states, top_n_KNN_states = screen_classifier_KNN.run_knn_query_states(dynamicXML_embedding_autoencoder,
                                                                                  usage_model.states)

        screenIR_MLP_all, top_n_screenIR_MLP_all = screen_classifier_MLP.classify_allapp_as_training(
            dynamicXML_embedding_autoencoder, N)

        screenIR_MLP_states, top_n_screenIR_MLP_states = screen_classifier_MLP.train_and_classify_for_states(AUT,
                                                                                                             dynamicXML_embedding_autoencoder,
                                                                                                             N,
                                                                                                             usage_model.states)

        # screenIR_MLP_states_all, top_n_screenIR_MLP_states_all = screen_classifier_MLP.train_and_classify_for_states('allapps',
        #                                                                                                dynamicXML_embedding_autoencoder,
        #                                                                                                N, usage_model.states)

        if REMAUI_embedding_autoencoder is not None:
            REMAUI_KNN_states, REMAUI_top_n_KNN_states = screen_classifier_KNN.run_knn_query_states(
                REMAUI_embedding_autoencoder,
                usage_model.states)
            REMAUI_KNN, REMAUI_top_n_KNN = screen_classifier_KNN.run_knn_query(REMAUI_embedding_autoencoder)
            REMAU_MLP, REMAUI_top_n_MLP = screen_classifier_MLP.classify(REMAUI_embedding_autoencoder, AUT, N)

            REMAUI_all, REMAUI_top_n_all = screen_classifier_MLP.classify_allapp_as_training(
                REMAUI_embedding_autoencoder, N)
            REMAUI_states, REMAUI_top_n_states = screen_classifier_MLP.train_and_classify_for_states(AUT,
                                                                                                     REMAUI_embedding_autoencoder,
                                                                                                     N,
                                                                                                     usage_model.states)
            REMAUI_states_all, REMAUI_top_n_states_all = screen_classifier_MLP.train_and_classify_for_states('allapps',
                                                                                                             REMAUI_embedding_autoencoder,
                                                                                                             N,
                                                                                                             usage_model.states)
        print('KNN:', screenIR_KNN, top_n_screenIR_KNN)
        if REMAUI_flag:
            print('REMAUI KNN:', REMAUI_KNN, REMAUI_top_n_KNN)
        print()
        print('MLP:', screenIR_MLP, top_n_screenIR_MLP)
        if REMAUI_flag:
            print('REMAUI MLP:', REMAU_MLP, REMAUI_top_n_MLP)
        print()
        print('MLP all training:', screenIR_MLP_all, top_n_screenIR_MLP_all)
        if REMAUI_flag:
            print('REMAUI all training:', REMAUI_all, REMAUI_top_n_all)
        print()
        print('MLP states partial training:', screenIR_MLP_states, top_n_screenIR_MLP_states)
        if REMAUI_flag:
            print('REMAUI states partial:', REMAUI_states, REMAUI_top_n_states)
        print()
        print('KNN states:', KNN_states, top_n_KNN_states)
        if REMAUI_flag:
            print('REMAUI KNN states:', REMAUI_KNN_states, REMAUI_top_n_KNN_states)
        print()
        # print('MLP states all apps:', screenIR_MLP_states_all, top_n_screenIR_MLP_states_all)
        if REMAUI_flag:
            print('REMAUI states all apps:', REMAUI_states_all, REMAUI_top_n_states_all)
        print()
        print('usage model states:', usage_model.states)
        print()
        all_ir_candidates = set(top_n_screenIR_KNN).union(set(top_n_screenIR_MLP_states))
        all_ir_candidates = list(all_ir_candidates)
        ## filter out results that's NOT from usage model's states and should be excluded
        for ir in all_ir_candidates:
            if (ir not in usage_model.states) or (
                    ir in ['sign_up_birthday', 'signin_amazon', 'signin_fb', 'signin_google', 'signin_google_popup']):
                all_ir_candidates.remove(ir)

        print('filtered top N:', all_ir_candidates)
        print()
        print('Activity:', self.activity)
        activity_wordlist = self.activity.replace('.', ' ').lower().strip()
        print('Activity wordlist:', activity_wordlist)
        print()
        text_info_strs = set()
        text_info_strs.add(activity_wordlist)
        for element in self.nodes:
            for key in element.data:
                if key == 'text':
                    text_info_strs.add(element.data[key])
                if key == 'content-desc':
                    text_info_strs.add(element.data[key])
                if key == 'resource-id':
                    text_info_strs.add(element.data[key].split('/')[-1])
                if key == 'id':
                    text_info_strs.add(element.data[key])
        text_info_strs = " ".join(text_info_strs)
        print('text info:', text_info_strs)

        if text_sim_w2v is not None and text_sim_bert is not None:
            print('-----textual similarities-----')
            for ir_candidate in all_ir_candidates:
                wordlist = self.get_wordlist(ir_candidate)
                print('wordlist:', wordlist)
                # wordlist = ir_candidate
                bert_sim = text_sim_bert.calc_similarity(text_info_strs, wordlist)
                w2v_sim = text_sim_w2v.calc_similarity(text_info_strs, wordlist)
                print(ir_candidate, 'BERT:' + str(bert_sim), 'W2V:' + str(w2v_sim))



    def get_screenIR(self, eval_results, AUT, usage_model, text_sim_w2v, text_sim_bert, REMAUI_flag, true_IR=None):

        # save autoencoder embeddings to files
        dynamicXML_embedding_autoencoder = self.get_dynamic_embedding()
        REMAUI_embedding_autoencoder = None
        if REMAUI_flag:
            REMAUI_embedding_autoencoder = self.get_REMAUI_embedding()


        if true_IR is not None: # using true IR to generate tests (disable screen classifiers)
            XML_basename = os.path.basename(os.path.normpath(self.UIXML_path)).replace('.xml', '')
            if XML_basename in eval_results.keys():
                eval_results[XML_basename]['true_screen_IR'] = true_IR
            else:
                eval_results[XML_basename] = {}
                eval_results[XML_basename]['true_screen_IR'] = true_IR
            return true_IR

        else:
            self.explore_screen_classifiers(dynamicXML_embedding_autoencoder, REMAUI_embedding_autoencoder,
                                   AUT, usage_model, text_sim_w2v, text_sim_bert, REMAUI_flag, true_IR)

        return None

    def get_model(self, app):
        model_path = "../4_dynamic_generation/screen_classifier/screen_classifier_models_pretrain_scratch/" + app + "_screen_model"
        screen_classifier = ScreenClassifier()
        screen_classifier.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        screen_classifier.eval()
        return screen_classifier

    def get_label_with_fs_model(self, classifier_model, layout_emb, text_emb):
        out = classifier_model(text_emb, layout_emb)
        y_pred_softmax = torch.log_softmax(out, dim=1)
        top_10 = torch.argsort(y_pred_softmax)[:, -10:]
        top_5 = torch.argsort(y_pred_softmax)[:, -5:]
        top_sorted = torch.argsort(y_pred_softmax)[:, -31:]
        _, y_pred = torch.max(y_pred_softmax, dim=1)
        return y_pred, top_5, top_10, top_sorted

    def get_screen_IR(self, AUT, bert, words, usage_model):
        REMAUI_embedding_autoencoder = torch.Tensor(self.get_REMAUI_embedding())
        ocr_text_embedding = self.get_ocr_text_embedding(bert, words)
        screen_classifier = self.get_model(AUT)
        remaui_ocr_top1, remaui_ocr_top5, remaui_ocr_top10, top_sorted = self.get_label_with_fs_model(screen_classifier, REMAUI_embedding_autoencoder, ocr_text_embedding)

        for screen_id in remaui_ocr_top1:
            top_1_tag = self.get_screen_tag(screen_id)

        top_5_tags = []
        for screen_id in remaui_ocr_top5[0]:
            top_5_tags.append(self.get_screen_tag(screen_id))

        top_10_tags = []
        for screen_id in remaui_ocr_top10[0]:
            top_10_tags.append(self.get_screen_tag(screen_id))

        print(top_sorted)
        all_tags = []
        for screen_id in top_sorted[0]:
            all_tags.append(self.get_screen_tag(screen_id))

        new_top_5 = []
        added = 0
        i = 1
        while added<5:
            if all_tags[-1*i] in usage_model.states:
                new_top_5.append(all_tags[-1*i])
                added += 1
            i+=1

        # print(new_top_5)

        return top_1_tag, new_top_5, top_10_tags


    def get_wordlist(self, screenIR):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        wordlist_dir = os.path.join(current_dir_path, '..', '..', 'IR', 'label_texts')
        wordlist_path = os.path.join(wordlist_dir, screenIR + '.txt')
        if os.path.exists(wordlist_path):
            file = open(wordlist_path, "r")
            return file.read().lower()

        return screenIR # if no wordlist is found for the screenIR, use the screenIR name itself as the wordlist


    def find_widget_to_trigger(self, widgetIR):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        widget_ir_csv = os.path.join(current_dir_path, '..', '..', 'IR', 'widget_ir.csv')
        widget_df = pd.read_csv(widget_ir_csv)
        row_found = widget_df.loc[widget_df['ir'] == widgetIR]

        if len(row_found) == 0:
            print('widget IR', widgetIR)
            raise ValueError('no widget IR found')
        else:
            widget_type = row_found['widget_type'].values[0]

        input_element_type = ['EditText', 'AutoCompleteTextView', 'Spinner']
        element_candidates = []
        for element in self.nodes:
            if element.interactable:

                element_type = element.get_element_type().split('.')[-1]
                if (widget_type == 'input' and element_type not in input_element_type) \
                        or (pd.isna(widget_type) and element_type in input_element_type):
                    continue
                element_candidates.append(element)
        for element in element_candidates:
            image = PIL.Image.open(element.path_to_screenshot)
            image.show()
            # element.data # has content-desc, resource-id, text
        i = int(input('widget index to trigger\n'))
        # kill all the images opened by Preview
        for proc in psutil.process_iter():
            # print(proc.name())
            if proc.name() == 'Preview':
                proc.kill()
        if i >= len(element_candidates):
            return None
        return element_candidates[i]

    def find_widget_to_trigger(self, widgetIR, screenIR, bert, app_name):
        widget_classifier = UIEmbedder()
        model_path = "../4_dynamic_generation/widget_classifier/widget_classifiers_pretrained/"+app_name+"_widget_model_with_image"
        widget_classifier.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        widget_classifier.eval()

        top_candidates = []
        secondary_candidates = []
        heuristic_matches = []
        predicted_irs = {}
        for element in self.nodes:
            if element.interactable:
                text = element.get_processed_textual_info()
                text_embedding = torch.as_tensor(bert.encode(text))
                text_embedding = text_embedding.resize(1, 768)
                # print("text:")
                # print(text)
                screen_id = torch.tensor([classifier_utils.get_screen_id(screenIR)])
                location_id = torch.tensor([classifier_utils.convert_bounds_to_screen_zone(element.get_middle_point())])
                element_type = element.get_element_type().split('.')[-1]
                # print(element_type)
                if element_type == "ScrollView" or element_type == "ViewGroup" or element_type == "RecyclerView":
                    continue
                if (("email" in text) and element_type == "EditText") or (("password" in text) and element_type == "EditText"):
                    continue
                print("-----")
                print(widgetIR)
                print(text)
                print(element.get_exec_id_val())
                if self.look_for_exact_match(widgetIR, text):
                    if widgetIR == "search_bar":
                        if element_type == "EditText":
                            heuristic_matches.append(element)
                            continue
                    elif widgetIR == "to_search":
                        if element_type != "EditText":
                            heuristic_matches.append(element)
                            continue
                    else:
                        heuristic_matches.append(element)
                        continue
                if self.check_for_top_match_heuristics(widgetIR, screenIR, element):
                    top_candidates.append(element)
                type_id = torch.tensor([classifier_utils.convert_class_to_text_label(element_type)])
                image = classifier_utils.convert_image_to_input_vector(element.path_to_screenshot)
                image = image.resize(1, 3, 244, 244)
                out = widget_classifier(text_embedding, type_id, screen_id, image, location_id)

                y_pred_softmax = torch.log_softmax(out, dim=1)
                top_n = torch.argsort(y_pred_softmax)[:, -5:]
                _, y_pred_tags = torch.max(y_pred_softmax, dim=1)
                top_5 = classifier_utils.get_widget_tag(top_n[0])
                top_1 = classifier_utils.get_widget_tag(y_pred_tags)
                # print(top_5)
                # print(top_1)

                if widgetIR in top_1:
                    top_candidates.append(element)
                elif widgetIR in top_5:
                    secondary_candidates.append(element)

        return top_candidates, secondary_candidates, heuristic_matches


    def look_for_exact_match(self, trigger, text):
        if trigger in text:
            return True
        if "_" in trigger:
            v1 = trigger.replace("_", "")
            if v1 in text:
                return True
            v2 = trigger.replace("_", " ")
            if v2 in text:
                return True
        if "_" in trigger:
            trigger_words = trigger.split("_")
            for word in trigger_words:
                if word in ["by", "i", "multi", "to", "sign", "in", "up", "or"]:
                    continue
                if word in text:
                    return True
        if trigger == "to_signin_or_signup":
            if ("sign in" in text) or ("sign up" in text) or ("signin" in text) or ("signup" in text) or ("get started" in text) or ("register" in text) or ("create account" in text) or ("login" in text):
                return True
            if ("google" in text) or ("facebook" in text):
                return False
        if trigger == "sign_up":
            if ("register" in text) or ("create account" in text) or ("join" in text):
                return True
        if trigger == "continue" or trigger == "apply" or trigger == "bypass":
            if ("ok" in text) or ("accept" in text) or ("deny" in text) or ("skip" in text) or ("next" in text):
                return True
        if trigger == "menu":
            if ("drawer" in text) or ("navigation" in text) or ("option" in text):
                return True
        if trigger == "to_search" or trigger == "search_bar":
            if "search" in text:
                return True
        if trigger == "cart":
            if "bag" in text:
                return True
        if trigger == "help":
            if ("guide" in text) or ("question" in text) or ("faq" in text) or ("how" in text):
                return True
        if "bookmark" in trigger:
            if "bookmark" in text or "save" in text:
                return True
        if "apply" in trigger:
            if "done" in text or "submit" in text or "send" in text:
                return True
        if trigger == "category":
            if ("sections" in text) or ("topics" in text):
                return True
        if "item" in trigger:
            if "product" in text:
                return True
        return False

    def check_for_top_match_heuristics(self, widgetIR, screenIR, element):
        if screenIR == "menu":
            if element.is_a_list_item():
                return True
        if screenIR == "items" or screenIR == "category":
            if widgetIR == "item_i" or widgetIR == "category_i":
                if element.is_a_list_item():
                    print(element.get_exec_id_val())
                    return True


if __name__ == '__main__':
    state = State('')
    state.UIXML_path = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models/1-SignIn/dynamic_output/etsy/screenshots/0-1.xml'
    # state.nodes = ['a', 'b']
    print('all done! :)')
