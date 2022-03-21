import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET

final_data_dir = os.path.abspath('/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts')
screenIR_file = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/IR/screen_ir.csv'
widgetIR_file = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/IR/widget_ir.csv'

def count_files():
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        totalDir = 0
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                totalDir += 1
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(totalDir))

def count_labels_per_usage():
    total_screen_label = 0
    total_widget_label = 0
    screenIRs = []
    widgetIRs = []
    for file in glob.glob(final_data_dir + '/*/LS-annotations.csv'):
        df = pd.read_csv(file)
        screenIRs += df['tag_screen'].unique().tolist()
        widgetIRs += df['tag_widget'].unique().tolist()
        total_screen_label += df.count(axis=0)['tag_screen']
        total_widget_label += df.count(axis=0)['tag_widget']
    print('screen total labels:', total_screen_label)
    print('widget total labels:', total_widget_label)
    print('total screen IRs', len(set(screenIRs)), set(screenIRs))
    print('total widget IRs', len(set(widgetIRs)), set(widgetIRs))

    screen_df = pd.read_csv(screenIR_file)
    widget_df = pd.read_csv(widgetIR_file)
    screenIR_def = screen_df['ir'].unique().tolist()
    widgetIR_def = widget_df['ir'].unique().tolist()
    print('screen diff:', set(screenIRs) - set(screenIR_def))
    print('screen diff other way:', set(screenIR_def) - set(screenIRs))
    print('widget diff:', set(widgetIRs) - set(widgetIR_def))
    print('widget diff other way:', set(widgetIR_def) - set(widgetIRs))
    return screenIRs, widgetIRs, screenIR_def, widgetIR_def


def count_subject_apps():
    total_apps = {}
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        apps = {}
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                appName = os.path.basename(os.path.normpath(file)).split('-')[0].lower()
                if appName in apps.keys():
                    apps[appName] += 1
                else:
                    apps[appName] = 1
                if appName in total_apps.keys():
                    total_apps[appName] += 1
                else:
                    total_apps[appName] = 1
        print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(apps))
        # print(os.path.basename(os.path.normpath(sub_dir)) + '\t' + str(len(apps)) + '\t' + str(apps))
    print('total apps:', total_apps)
    print('total app count', len(total_apps))
    count = 0
    for key in total_apps.keys():
        count += total_apps[key]
    print('total traces count', count)

def find_overlapping_apps():
    i = 0
    overlapping_apps = set()
    for sub_dir in sorted(glob.glob(os.path.join(final_data_dir, '*'))):
        apps_per_usage = set()
        for file in glob.glob(os.path.join(sub_dir, '*')):
            if os.path.isdir(file):
                appName = os.path.basename(os.path.normpath(file)).split('-')[0].lower()
                apps_per_usage.add(appName)
        if i == 0:
            overlapping_apps = apps_per_usage
        else:
            overlapping_apps = overlapping_apps.intersection(apps_per_usage)
        i += 1
        print('apps in this usage', apps_per_usage, os.path.basename(os.path.normpath(sub_dir)))
        print('overlapping apps', overlapping_apps)

def read_IRs_from_LS_interface():
    interface_xml = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/2_ir_classification/label_interface.xml'
    tree = ET.parse(interface_xml)
    root = tree.getroot()
    xml_widget_IRs = set()
    xml_screen_IRs = set()
    for node in root.findall('./'):
        if node.attrib['name'] == 'tag_screen':
            for choice in node.findall('./'):
                xml_screen_IRs.add(choice.attrib['value'])
        elif node.attrib['name'] == 'tag_widget':
            for choice in node.findall('./'):
                xml_widget_IRs.add(choice.attrib['value'])
    return xml_screen_IRs, xml_widget_IRs

def get_labels_from_final_csv():
    final_label = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/final_labels/final_labels_all.csv'

    df = pd.read_csv(final_label)
    screenIRs = df['tag_screen'].unique().tolist()
    widgetIRs = df['tag_widget'].unique().tolist()
    print('total screen IRs', len(set(screenIRs)), set(screenIRs))
    print('total widget IRs', len(set(widgetIRs)), set(widgetIRs))

    screen_df = pd.read_csv(screenIR_file)
    widget_df = pd.read_csv(widgetIR_file)
    screenIR_def = screen_df['ir'].unique().tolist()
    widgetIR_def = widget_df['ir'].unique().tolist()
    print('screen diff:', set(screenIRs) - set(screenIR_def))
    print('screen diff other way:', set(screenIR_def) - set(screenIRs))
    print('widget diff:', set(widgetIRs) - set(widgetIR_def))
    print('widget diff other way:', set(widgetIR_def) - set(widgetIRs))
    return screenIRs, widgetIRs, screenIR_def, widgetIR_def

if __name__ == '__main__':
    xml_screen_IRs, xml_widget_IRs = read_IRs_from_LS_interface()
    labeled_screenIRs, labeled_widgetIRs, screenIR_def, widgetIR_def = get_labels_from_final_csv()
    print('aaa', set(xml_widget_IRs) - set(widgetIR_def))
    print('bbb', set(widgetIR_def) - set(xml_widget_IRs))
    print('def == xml?', set(xml_widget_IRs) == set(widgetIR_def))
    print('ccc', set(xml_widget_IRs) - set(labeled_widgetIRs))
    print('ddd', set(labeled_widgetIRs) - set(xml_widget_IRs))
    print('all done! :)')