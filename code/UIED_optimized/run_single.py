from os.path import join as pjoin
import cv2
import os


def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))


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

    # set input image path
    input_path_img = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/ir_data/6pm-video-signin-3-bbox-2890-screen.jpg'
    output_root = 'data/output/'

    resized_height = resize_height_by_longest_edge(input_path_img)
    print('starting...')

    is_ip = True
    is_clf = True
    is_ocr = True
    is_merge = True

    if is_ocr:
        print('ocr...')
        import detect_text_east.ocr_east as ocr
        import detect_text_east.lib_east.eval as eval
        os.makedirs(pjoin(output_root, 'ocr'), exist_ok=True)
        models = eval.load()
        ocr.east(input_path_img, output_root, models, key_params['max-word-inline-gap'],
                 resize_by_height=resized_height, show=False)

    if is_ip:
        print('ip...')
        import detect_compo.ip_region_proposal as ip
        os.makedirs(pjoin(output_root, 'ip'), exist_ok=True)
        # switch of the classification func
        classifier = None
        if is_clf:
            classifier = {}
            from cnn.CNN import CNN
            # classifier['Image'] = CNN('Image')
            classifier['Elements'] = CNN('Elements')
            # classifier['Noise'] = CNN('Noise')
        ip.compo_detection(input_path_img, output_root, key_params,
                           classifier=classifier, resize_by_height=resized_height, show=False)

    if is_merge:
        print('merge...')
        import merge_optimized
        name = input_path_img.split('/')[-1][:-4]
        compo_path = pjoin(output_root, 'ip', str(name) + '.json')
        ocr_path = pjoin(output_root, 'ocr', str(name) + '.json')
        merge_optimized.incorporate(input_path_img, compo_path, ocr_path, output_root, params=key_params,
                          resize_by_height=resized_height, show=False)
