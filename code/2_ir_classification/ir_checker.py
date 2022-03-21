import pandas as pd

def check_screen(ir_screen, labeled_files):
    for file in labeled_files:
        df = pd.read_csv(file)
        rows = df.loc[df['tag_screen'] == ir_screen]
        if len(rows) != 0:
            return True
    return False

def check_widget(ir_widget, labeled_files):
    for file in labeled_files:
        df = pd.read_csv(file)
        rows = df.loc[df['tag_widget'] == ir_widget]
        if len(rows) != 0:
            return True
    return False

def count_IRs(labeled_files):
    df_array = []
    for file in labeled_files:
        df = pd.read_csv(file)
        df_array.append(df)
    merged_df = pd.concat(df_array)
    print(merged_df.nunique())


if __name__ == '__main__':
    labeled_files = ['/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/LS-annotations.csv',
                     '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/1-SignIn/LS-annotations.csv']
    screen_to_check = 'sign_up_gmail'
    widget_to_check = 'cart_quantity_0'
    if check_widget(widget_to_check, labeled_files):
        print('widget: YES')
    else:
        print('widget: NO')
    if check_screen(screen_to_check, labeled_files):
        print('screen: YES')
    else:
        print('screen: NO')
    count_IRs(labeled_files)