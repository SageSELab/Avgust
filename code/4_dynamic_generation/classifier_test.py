import os, sys, pickle, time
import explorer

from bert_similarity_calc import SimilarityCalculator_BERT
from text_similarity_calculator import SimilarityCalculator_W2V
from App_Config import *

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))

from global_config import *

def test_screen_classifier(AUT, usage_name, desiredCapabilities, text_sim_flag, REMAUI_flag):
    usage_model_path = os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', usage_name, 'usage_model-' + AUT + '.pickle')

    app_explorer = explorer.Explorer(desiredCapabilities)
    text_sim_w2v = None
    text_sim_bert = None
    if text_sim_flag:
        text_sim_w2v = SimilarityCalculator_W2V()
        text_sim_bert = SimilarityCalculator_BERT()
    usage_model = pickle.load(open(usage_model_path, 'rb'))
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(current_dir_path, 'tmp_screen_test')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    while True:
        # time.sleep(2)
        current_state = app_explorer.extract_state(output_dir)
        current_state.print_state()
        current_state.get_screenIR(AUT, usage_model, text_sim_w2v, text_sim_bert, REMAUI_flag)
        user_input = input('enter q to exit')
        if user_input == 'q':
            break

if __name__ == '__main__':
    # appPackage and appActivity can be found here for shooping apps: https://github.com/felicitia/UsageTesting-Repo/blob/master/shopping_app_info.csv
    # here for news apps: https://github.com/felicitia/UsageTesting-Repo/blob/master/news_app_info.csv
    AUT = Etsy()
    # AUT = Abc()
    # AUT = SixPM()
    # AUT = Home()
    usage_name = '1-SignIn'
    # usage_name = '18-TextSize'
    # usage_name = '3-Category'
    test_screen_classifier(AUT.appname, usage_name, AUT.desiredCapabilities, text_sim_flag=False, REMAUI_flag=True)
