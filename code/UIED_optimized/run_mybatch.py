from os.path import join as pjoin
import cv2
import os
import glob
import detect_text_east.ocr_east as ocr
import detect_text_east.lib_east.eval as eval
import detect_compo.ip_region_proposal as ip
import merge_optimized
from cnn.CNN import CNN

def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))

def run_single(input_path_img, output_dir, models):
    # input_path_img = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-1/ir_data/bbox-0189-screen.jpg'
    single_output = os.path.join(output_dir, 'result.jpg')
    if os.path.exists(single_output):
        return

    print('running', input_path_img)

    resized_height = resize_height_by_longest_edge(input_path_img)

    if is_ocr:
        print('ocr...')
        os.makedirs(pjoin(output_dir, 'ocr'), exist_ok=True)
        ocr.east(input_path_img, output_dir, models, key_params['max-word-inline-gap'],
                 resize_by_height=resized_height, show=False)

    if is_ip:
        print('ip...')
        os.makedirs(pjoin(output_dir, 'ip'), exist_ok=True)
        # switch of the classification func
        classifier = None
        if is_clf:
            classifier = {}
            # classifier['Image'] = CNN('Image')
            classifier['Elements'] = CNN('Elements')
            # classifier['Noise'] = CNN('Noise')
        ip.compo_detection(input_path_img, output_dir, key_params,
                           classifier=classifier, resize_by_height=resized_height, show=False)

    if is_merge:
        print('merge...')
        name = input_path_img.split('/')[-1][:-4]
        compo_path = pjoin(output_dir, 'ip', str(name) + '.json')
        ocr_path = pjoin(output_dir, 'ocr', str(name) + '.json')
        merge_optimized.incorporate(input_path_img, compo_path, ocr_path, output_dir, params=key_params,
                          resize_by_height=resized_height, show=False)


def run_batch(usage_root_dir, output_root_dir):
    models = eval.load()
    usage_name = os.path.basename(os.path.normpath(usage_root_dir))
    for ir_data_dir in glob.glob(usage_root_dir + '/*/ir_data_auto/'):
        app_root_name = os.path.basename(os.path.normpath(ir_data_dir.replace('ir_data_auto/', '')))
        for img in glob.glob(ir_data_dir + '*-screen.jpg'):
            output_dir = os.path.join(output_root_dir, usage_name, app_root_name, os.path.basename(img).split('.')[0])
            run_single(img, output_dir, models)

if __name__ == '__main__':

    '''
        ele:min-grad: gradient threshold to produce binary map         
        ele:ffl-block: fill-flood threshold
        ele:min-ele-area: minimum area for selected elements 
        ele:merge-contained-ele: if True, merge elements contained in others
        text:max-word-inline-gap: words with smaller distance than the gap are counted as a line
        text:max-line-gap: lines with smaller distance than the gap are counted as a paragraph

        Tips:
        1. Larger *min-grad* produces fine-grained binary-map while prone to over-segment element to small pieces
        2. Smaller *min-ele-area* leaves tiny elements while prone to produce noises
        3. If not *merge-contained-ele*, the elements inside others will be recognized, while prone to produce noises
        4. The *max-word-inline-gap* and *max-line-gap* should be dependent on the input image size and resolution

        mobile: {'min-grad':4, 'ffl-block':5, 'min-ele-area':50, 'max-word-inline-gap':6, 'max-line-gap':1}
        web   : {'min-grad':3, 'ffl-block':5, 'min-ele-area':25, 'max-word-inline-gap':4, 'max-line-gap':4}
    '''
    key_params = {'min-grad':4, 'ffl-block':5, 'min-ele-area':50, 'merge-contained-ele':True,
                  'max-word-inline-gap':6, 'max-line-gap':1}
    is_ip = True
    is_clf = True
    is_ocr = True
    is_merge = True

    usage_root_dir = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/SignIn'
    output_root_dir = '/Users/XXX/Documents/Research/UsageTesting/Develop/UIED2.3-output-optimized'

    run_batch(usage_root_dir, output_root_dir)