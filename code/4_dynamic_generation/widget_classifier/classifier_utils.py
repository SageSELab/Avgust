from torchvision import transforms
from PIL import Image
import os
import json
import torch

def convert_class_to_text_label(widget_type):
    lookup_class_label_dict = {"AdView": 1, "HtmlBannerWebView":1, "AdContainer":1, "ActionBarOverlayLayout": 2, "TabLayout": 2, "TabLayout$SlidingTabStrip": 2,  "TabLayout$TabView": 2, "LinearLayout": 2, "FitWindowsLinearLayout": 2, "CustomScreenLinearLayout": 2, "AppBarLayout": 2, "FrameLayout": 2, "ContentFrameLayout": 2, "FitWindowsFrameLayout": 2, "NoSaveStateFrameLayout": 2, "RelativeLayout": 2, "TableLayout": 2, "BottomTagGroupView": 3, "BottomBar": 3, "ButtonBar": 4, "CardView": 5, "CheckBox": 6, "CheckedTextView":6, "DrawerLayout": 7, "DatePicker": 8, "ImageView": 9, "ImageButton": 10, "GlyphView": 10, "AppCompactButton": 10, "AppCompactImageButton": 10, "ActionMenuItemView":10, "ActionMenuItemPresenter":10, "EditText": 11, "SearchBoxView": 11, "AppCompatAutoCompleteTextView": 11, "TextView": 11, "TextInputLayout": 11,  "ListView": 12, "RecyclerView": 12, "ListPopUpWindow": 12, "tabItem": 12, "GridView": 12, "MapView": 13, "SlidingTab": 14, "NumberPicker": 15, "Switch": 16, "SwitchCompat":16, "ViewPageIndicatorDots": 17, "PageIndicator": 17, "CircleIndicator": 17, "PagerIndicator": 17, "RadioButton": 18, "CheckedTextView": 18, "SeekBar": 19, "Button": 20, "TextView": 20, "ToolBar": 21, "Toolbar": 21, "TitleBar": 21, "ActionBar": 21, "VideoView": 22, "WebView": 23}
    the_class_of_text = widget_type
    if lookup_class_label_dict.get(the_class_of_text):
        return lookup_class_label_dict.get(the_class_of_text)
    else:
        for key, val in lookup_class_label_dict.items():
            if the_class_of_text.endswith(key):
                return val
            if the_class_of_text.startswith(key):
                return val
        return 0


def convert_bounds_to_screen_zone(bounds):
    zones = {1: [0, 0, 135, 315], 2: [135, 0, 945, 315], 3: [945, 0, 1080, 315],
             7: [0, 1736, 135, 1920], 8: [135, 1736, 945, 1920], 9: [945, 1736, 1080, 1920],
             4: [0, 315, 135, 1736], 5: [135, 315, 945, 1736], 6: [945, 315, 1080, 1736]}

    x = bounds[0]
    y = bounds[1]
    for zone, zone_bounds in zones.items():
        if zone_bounds[0] <= x <= zone_bounds[2] and zone_bounds[1] <= y <= zone_bounds[3]:
            return zone
    return 0


def convert_image_to_input_vector(image_path):
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(min(244, 256)),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406),
                             (0.229, 0.224, 0.225))])

    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    return image

def get_screen_id(screen_tag):
    with open("../4_dynamic_generation/widget_classifier/screen_dict.json") as screen_dict_file:
        screen_dict = json.load(screen_dict_file)
        screen_id = screen_dict[screen_tag]
    return screen_id

def get_widget_tag(widget_ids):
    widget_tags = []
    with open("../4_dynamic_generation/widget_classifier/widget_dict.json") as widget_dict_file:
        widget_dict = json.load(widget_dict_file)
        for widget_id in widget_ids:
            widget_tag = widget_dict[str(int(widget_id))]
            widget_tags.append(widget_tag)

    return widget_tags


