import pickle
import sys
import os
import torch
import cv2
import pytesseract
import PIL
import nltk
import json
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation', 'screen_classifier'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation', 'autoencoder'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation', 'autoencoder', 'aeSrc'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation', 'autoencoder_KNN'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation', 'autoencoder_MLP'))

from model import ScreenClassifier
from global_config import *
from createSilhouette import createUIImage
from getEmbeddings import getAEembeddings
from REMAUI_XML2JSON_convertor import convert_to_json_REMAUI
from screen_classifier_KNN_autoencoder import KNN_screen_classifier
from MLP_classify import MLP_ScreenClassifierForAUT

bert = SentenceTransformer('bert-base-nli-mean-tokens').to('cpu')
nltk.download('words')
nltk.download('punkt')
words = set(nltk.corpus.words.words())
os.environ["TOKENIZERS_PARALLELISM"] = "false"
recorded_data_path = FINAL_ARTIFACT_ROOT_DIR + "/output/Final Eval Results"
output_path = FINAL_ARTIFACT_ROOT_DIR + "/output/screen_classifier_results"
device = 'cpu'
embeddings_path = "../4_dynamic_generation/autoencoder_KNN/autoencoder_embeddings"
labels_path = ["../4_dynamic_generation/autoencoder_KNN/final_labels_all.csv","../4_dynamic_generation/autoencoder_KNN/augmented_labels.csv"]

def OCR(path, words_only=True):
    image = cv2.imread(path)
    image = cv2.medianBlur(image, 3)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(PIL.Image.fromarray(image))
    text = text.split()
    return [word.lower() for word in text]


def process_text_data(raw_data):
    remove_none_english = [w for w in raw_data if w in words]
    sentence = " ".join(remove_none_english)
    return sentence


def process_dynamic_text_data(raw_data):
    raw_words = []
    for text in raw_data:
        text = text.replace("/", " ")
        raw_words += (word_tokenize(text.lower()))
    remove_none_english = [w for w in raw_words if w in words]
    sentence = " ".join(remove_none_english)
    return sentence


def traverse_tree(node, text_data):
    if "text" in node.keys():
        text_data.append(node["text"])
    if "children" in node.keys():
        for child in node["children"]:
            traverse_tree(child, text_data)


def get_text_from_json(json_path):
    with open(json_path) as json_file:
        dynamic_data = json.load(json_file)
        root_node = dynamic_data["activity"]["root"]
        text_data = []
        traverse_tree(root_node, text_data)
    return text_data


def get_screen_id(screen_tag):
    screen_dict_path = "../4_dynamic_generation/screen_classifier/screen_dict.json"
    with open(screen_dict_path) as screen_dict_file:
        screen_dict = json.load(screen_dict_file)
    return screen_dict[screen_tag]


def get_label_with_fs_model(classifier_model, layout_emb, text_emb):
    out = classifier_model(text_emb, layout_emb)
    y_pred_softmax = torch.log_softmax(out, dim=1)
    top_10 = torch.argsort(y_pred_softmax)[:, -10:]
    top_5 = torch.argsort(y_pred_softmax)[:, -5:]
    _, y_pred = torch.max(y_pred_softmax, dim=1)
    return y_pred, top_5, top_10


def get_model(app):
    model_path = "../4_dynamic_generation/screen_classifier/screen_classifier_models_pretrain_scratch/" + app + "_screen_model"
    screen_classifier = ScreenClassifier()
    screen_classifier.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    screen_classifier.eval()
    return screen_classifier


def get_remaui_ae_embedding(xml_path):
    REMAUI_error = convert_to_json_REMAUI(xml_path)
    while REMAUI_error is not None:
        print(xml_path)
        print('REMAUI error:', REMAUI_error)
        input('please fix the XML and continue')
        REMAUI_error = convert_to_json_REMAUI(xml_path)
    createUIImage(xml_path.replace('xml', 'json'))
    REMAUI_embedding = torch.Tensor(getAEembeddings(os.path.dirname(xml_path), xml_path.replace('.xml', '-layout.jpg')))
    return REMAUI_embedding


def get_dynamic_xml_embedding(artifact_path_prefix, id):
    autoencoder_embedding = torch.Tensor(
        pickle.load(open(artifact_path_prefix + "/" + id + "-dynamicEmbedding.pickle", 'rb')))
    return autoencoder_embedding


def get_ocr_text_embedding(screenshot_path):
    text = OCR(screenshot_path)
    processed_ocr_text = process_text_data(text)
    text_embedding = torch.as_tensor(bert.encode(processed_ocr_text),
                                     device=device).reshape(1,
                                                            768)
    return text_embedding


def get_dynamic_text_embedding(json_path):
    dynamic_text = get_text_from_json(json_path)
    processed_dynamic_text = process_dynamic_text_data(dynamic_text)
    text_embedding = torch.as_tensor(bert.encode(processed_dynamic_text),
                                     device=device).reshape(1,
                                                            768)
    return text_embedding


def evaluate_dynamic_screen_classifiers():
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    correct_d_top_1 = 0
    correct_d_top_5 = 0
    correct_d_top_10 = 0
    correct_ro_top_1 = 0
    correct_ro_top_5 = 0
    correct_ro_top_10 = 0
    correct_d_KNN_top_5 = 0
    correct_d_KNN_top_1 = 0
    correct_r_KNN_top_5 = 0
    correct_r_KNN_top_1 = 0
    correct_d_mlp_top_5 = 0
    correct_d_mlp_top_1 = 0
    correct_r_mlp_top_5 = 0
    correct_r_mlp_top_1 = 0
    all_count = 0

    screen_classifier_MLP = MLP_ScreenClassifierForAUT(autoencoder=True)

    for usage in os.listdir(recorded_data_path):
        if usage == ".DS_Store":
            continue

        if not os.path.isdir(os.path.join(output_path, usage)):
            os.makedirs(os.path.join(output_path, usage))
            for app in os.listdir(os.path.join(recorded_data_path, usage)):
                if app == ".DS_Store":
                    continue
                else:
                    if app == "theguardian":
                        app = "guardian"
                    screen_classifier = get_model(app)
                    eval_json_path = os.path.join(recorded_data_path, usage, app, "eval_results.json")
                    print("**********")
                    print(app)
                    screen_classifier_KNN = KNN_screen_classifier(app, embeddings_path, labels_path, 5, 5)

                    with open(eval_json_path) as eval_json_file:
                        eval_json_data = json.load(eval_json_file)
                        for id in eval_json_data.keys():
                            if id == "usage_states" or id == "true_label_time":
                                continue

                            all_count += 1
                            correct_tag = eval_json_data[id]["true_screen_IR"]
                            correct_tag_id = get_screen_id(correct_tag)

                            artifact_path_prefix = os.path.join(recorded_data_path, usage, app, "screenshots")
                            screenshot_path = artifact_path_prefix + "/" + id + ".png"
                            json_path = artifact_path_prefix + "/" + id + ".json"
                            remaui_xml_path = os.path.join(recorded_data_path, usage, app, "REMAUI", id,
                                                           "activity_main.xml")

                            dynamic_xml_embedding = get_dynamic_xml_embedding(artifact_path_prefix, id)
                            remaui_embedding = get_remaui_ae_embedding(remaui_xml_path)
                            #
                            ocr_text_embedding = get_ocr_text_embedding(screenshot_path)
                            dynamic_text_embedding = get_dynamic_text_embedding(json_path)

                            screenIR_remaui_KNN, top_n_remaui_screenIR_KNN = screen_classifier_KNN.run_knn_query(
                                remaui_embedding)

                            screenIR_dyanmic_KNN, top_n_dynamic_screenIR_KNN = screen_classifier_KNN.run_knn_query(
                                dynamic_xml_embedding)

                            screenIR_dynamic_mlp, top_n_dynamic_screenIR_mlp = screen_classifier_MLP.classify(
                                dynamic_xml_embedding, app, 5)
                            screenIR_remaui_mlp, top_n_remaui_screenIR_mlp = screen_classifier_MLP.classify(
                                remaui_embedding, app, 5)

                            dynamic_top1, dynamic_top5, dynamic_top10 = get_label_with_fs_model(screen_classifier,
                                                                                                dynamic_xml_embedding,
                                                                                                dynamic_text_embedding)
                            remaui_ocr_top1, remaui_ocr_top5, remaui_ocr_top10 = get_label_with_fs_model(
                                screen_classifier, remaui_embedding, ocr_text_embedding)

                            if correct_tag_id in dynamic_top10:
                                correct_d_top_10 += 1
                            if correct_tag_id in dynamic_top5:
                                correct_d_top_5 += 1
                            if correct_tag_id in dynamic_top1:
                                correct_d_top_1 += 1
                            if correct_tag_id in remaui_ocr_top10:
                                correct_ro_top_10 += 1
                            if correct_tag_id in remaui_ocr_top5:
                                correct_ro_top_5 += 1
                            if correct_tag_id in remaui_ocr_top1:
                                correct_ro_top_1 += 1

                            if correct_tag == screenIR_dyanmic_KNN:
                                correct_d_KNN_top_1 += 1
                            if correct_tag in top_n_dynamic_screenIR_KNN:
                                correct_d_KNN_top_5 += 1
                            if correct_tag == screenIR_remaui_KNN:
                                correct_r_KNN_top_1 += 1
                            if correct_tag in top_n_remaui_screenIR_KNN:
                                correct_r_KNN_top_5 += 1

                            if correct_tag == screenIR_dynamic_mlp:
                                correct_d_mlp_top_1 += 1
                            if correct_tag in top_n_dynamic_screenIR_mlp:
                                correct_d_mlp_top_5 += 1
                            if correct_tag == screenIR_remaui_mlp:
                                correct_r_mlp_top_1 += 1
                            if correct_tag in top_n_remaui_screenIR_mlp:
                                correct_r_mlp_top_5 += 1

            print("from scratch dynamic results:")
            print("top1: " + str(correct_d_top_1 / all_count))
            print("top5: " + str(correct_d_top_5 / all_count))
            print("top10: " + str(correct_d_top_10 / all_count))

            print("--------------------------")
            print("from scratch ro results:")
            print("top1: " + str(correct_ro_top_1 / all_count))
            print("top5: " + str(correct_ro_top_5 / all_count))
            print("top10: " + str(correct_ro_top_10 / all_count))

            print("--------------------------")
            print("knn results dynamic:")
            print("top1: " + str(correct_d_KNN_top_1 / all_count))
            print("top5: " + str(correct_d_KNN_top_5 / all_count))

            print("--------------------------")
            print("knn results remaui:")
            print("top1: " + str(correct_r_KNN_top_1 / all_count))
            print("top5: " + str(correct_r_KNN_top_5 / all_count))

            print("--------------------------")
            print("mlp results dynamic:")
            print("top1: " + str(correct_d_mlp_top_1 / all_count))
            print("top5: " + str(correct_d_mlp_top_5 / all_count))

            print("--------------------------")
            print("mlp results remaui:")
            print("top1: " + str(correct_r_mlp_top_1 / all_count))
            print("top5: " + str(correct_r_mlp_top_5 / all_count))

            print("all count:")
            print(all_count)
            print("------------")
        else:
            print("already evaluated usage: " + usage)




if __name__ == '__main__':
    evaluate_dynamic_screen_classifiers()
