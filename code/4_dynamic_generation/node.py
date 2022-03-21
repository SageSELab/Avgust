import re
import dot_element_extract as dotElementExtractor
import nltk
import cv2
import pytesseract
import PIL


class Node:
    def __init__(self, id, attributes, interactable, interactions, num_of_children, tag, screenshot):
        self.id = id
        self.attributes = attributes
        self.interactable = interactable
        self.children = []
        self.parent = None
        self.interactions = interactions
        self.num_of_children = num_of_children
        self.tag = tag
        self.data = {}
        self.exec_identifier = {}
        self.sentence = []
        self.path_to_screenshot = screenshot

    def get_element_type(self):
        # print('element attributes' , self.attributes)
        # print('element tag', self.tag)
        # print('element interactions', self.interactions)
        if not self.tag is None and self.tag != '':
            return self.tag
        if self.attributes.has_key('class'):
            return self.attributes['class']
        else:
            raise ValueError('element tag and class are both not available. consider using ReDraw')

    def add_child(self, child_node):
        self.children.append(child_node)

    def add_data(self, key, value):
        self.data[key]=value

    def add_ocr_to_data(self):
        image = cv2.imread(self.path_to_screenshot)
        image = cv2.medianBlur(image, 3)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(PIL.Image.fromarray(image))
        text = text.split()
        word_list = [word.lower() for word in text]
        ocr_val = " ".join(word_list)
        self.data["ocr"] = ocr_val

    def get_node_date(self):
        return self.data

    def get_attribute(self, key):
        return self.attributes[key]

    def add_exec_identifier(self, key, value):
        self.exec_identifier[key] = value

    def get_exec_identifiers(self):
        return self.exec_identifier

    def add_to_sentence(self, val):
        if "is not selected" in val:
            val = re.sub('is not selected$', '', val)
        if "is selected" in val:
            val = re.sub('is selected$', '', val)
        if re.match('^(?=.*(Tab [1-9] of [1-9],)).*$', val):
            val = re.sub('Tab [1-9] of [1-9], ', '', val)
        val="Click on "+val
        self.sentence.append(val)

    def get_sentence(self, turn):
        if turn>len(self.sentence):
            return ""
        else:
            return self.sentence[turn-1]

    def get_path_to_screenshot(self):
        return self.path_to_screenshot


    def get_exec_id_type(self):
        if len(list(self.exec_identifier.keys()))==0:
            return "xPath"
        else:
            return list(self.exec_identifier.keys())[0]

    def get_exec_id_val(self):
        if len(list(self.exec_identifier.keys())) == 0:
            xpath = dotElementExtractor.findXPath(self.path_to_screenshot, self.get_path_to_dot())
            return xpath
        else:
            return self.exec_identifier[list(self.exec_identifier.keys())[0]]

    def get_middle_point(self):
        bounds = self.attributes["bounds"]
        points = bounds.split("][")
        tlx = float(points[0].split(",")[0][1:])
        tly = float(points[0].split(",")[1])
        brx = float(points[1].split(",")[0][1:])
        bry = float(points[0].split(",")[1])
        x = (tlx + brx) // 2
        y = (tly + bry) // 2
        return [x, y]

    def get_processed_textual_info(self):
        processed_data = []
        self.add_ocr_to_data()
        for key, value in self.data.items():
            if key == 'resource-id':
                value = value.split("/")[-1]
            value = value.replace("_", " ")
            value = self.camel_case_split(value)
            value = " ".join(value)
            tokens = [t.lower() for t in nltk.word_tokenize(value)]
            COMMON = {"selected", "tab", "not selected", "bar", "button", "menubar", "icon", "view", "ub", "container",
                      "row", "scroll", "horizontal", "imageview", "icn", "btn", "recycler", "module", "onclick", "fragment"}
            tokens_without_stop_common = [t for t in tokens if t not in COMMON]
            processed_data += tokens_without_stop_common

        processed_data = list(dict.fromkeys(processed_data))
        return " ".join(processed_data) + "."

    def camel_case_split(self, identifier):
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    def is_a_list_item(self):
        if self.parent.get_element_type().split('.')[-1] == "ListView" or self.parent.get_element_type().split('.')[-1] == "RecyclerView":
            return True
        return False

    def get_path_to_dot(self):
        dot_path = self.path_to_screenshot.rsplit("/",2)[0]
        dot_path = dot_path+"/graph.dot"
        return dot_path