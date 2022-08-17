"""
File to compute score with folder contain many file txt
"""
import argparse
from tkinter import image_names
from unittest import result
import numpy as np
import os
import pandas as pd
import json

def readFile():
    result = pd.read_excel('Data_Labeling.xlsx',  header=None)
    return result

def processing_data(list_string):
    list_item = list()
    list_item = [[item.upper(), '169000'] for item in list_string]
    return list_item

def convert_to_dict(file_test_path, index):
    """
    convert string to list
    """
    list_change = dict()
    try:
        list_string = pd.read_table(file_test_path, header= None)
        string = str(list_string.loc[index, 0]).replace("'", "\"")
        list_change = json.loads(string)
    except:
        pass
    return list_change

if __name__=='__main__':
    data_sample = readFile()
    """
    f1 score will be computed by: 
    input: image_menu - item name (name food - price) '002.jpeg' - ['gà nướng' - 10000]
    get name image -> compare item menu (name food, price) 
    if result[0] == get_image_name into file sample:
        name_food == data_sample[]

    prediction = tp/tp+tn
    tp = get_name_item in list_sample (++1)
    tn = get_name_item not in list_sample (++1)

    recall = tp/tp+fn
    tp = get_name_item in list_sample (++1)
    fn = sum_item_sample - tp

    f1 = 2 * (prediction * recall) / (prediction + recall) 

    this above f1 for an item menu

    sumary: average all f1 score 
    Score = 1/(count_image) [0.9 * f1]
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_folder", help="folder contains file txt have results ocr")
    args = parser.parse_args()

    score = list()

    test_folder_path = args.input_folder
    # try:

    for file in os.listdir(test_folder_path):
        test_path = os.path.join(test_folder_path, file)
        list_string = pd.read_table(test_path, header= None, sep='delimiter', encoding='utf8')
        print(list_string)

    #     list_string = convert_to_dict(test_path, 0)
    #     print(list_string)
    #     image_file = list_string['image_name']
    #     data_filter = data_sample[data_sample[0].isin([image_file])]     
    #     print(data_filter)

    #     prediction, recall, f1_score = 0.0, 0.0, 0.0
    #     tp_count = 0
    #     tn_count = 0

    #     prediction_translate, recall_translate, f1_score_translate = 0.0, 0.0, 0.0
    #     tp_count_translate = 0
    #     tn_count_translate = 0
    # # try:
    #     for item_ocr in list_string['infers']:
    #         data_filter_food = data_filter[data_filter[1].isin([item_ocr['food_name_vi']])]
    #         print(data_filter_food)
    # except:
    #     pass
    #             # if data_filter_food is not None:
                    # data_filter_price = data_filter_food[data_filter_food[3] == ([item_ocr['food_price']])]
                    # data_filder_translate = data_filter_food[data_filter_food[1] == ([item_ocr['food_name_en']])]
                    # print(data_filter_food.loc[0, 3])
                    # print("===============================================")
                    # print(data_filter_price)
            #         if data_filter_price.empty: #giả sử chưa quan tâm đến giá
            #             tn_count += 1
            #         else:
            #             tp_count += 1
                    
            #         if data_filder_translate.empty:
            #             tn_count_translate += 1
            #         else:
            #             tp_count_translate += 1
            #             # print(data_filter_food)
            # #prediction
            # try:
            #     prediction = 1.0*tp_count/(tp_count + tn_count)
            #     prediction_translate = 1.0*tp_count_translate/(tp_count_translate + tn_count_translate)
            # except:
            #     prediction = 0.0
            #     prediction_translate = 0.0
            # #recall
            # fn_count = data_filter.shape[0] - tp_count
            # fn_count_translate = data_filter.shape[0] - tp_count_translate
            # try:
            #     recall = 1.0*tp_count/(tp_count + fn_count)
            #     recall_translate = 1.0*tp_count_translate/(tp_count_translate + fn_count_translate)
            # except:
            #     recall = 0.0
            #     recall_translate = 0.0
            # #f1 score
            # try:
            #     f1_score = 2.0*(prediction * recall)/(prediction + recall)
            #     f1_score_translate = 2.0*(prediction_translate * recall_translate)/(prediction_translate + recall_translate)
            # except:
            #     f1_score = 0.0
            #     f1_score_translate = 0.0
            
            # # score_temp = f1_score*0.9 + f1_score_translate*0.1
            # score += [f1_score]

            # print(f'prediction {prediction}')
            # print(f'recall {recall}')
            # print(f'f1_score {f1_score}')
            # print(f'prediction trans {prediction_translate}')
            # print(f'recall trans{recall_translate}')
            # print(f'f1_score trans {f1_score_translate}')
            # print(score)
            # print("=====================================================================")
    # except Exception as e:
    #     print(e)
    #     pass

    # print(score)
    # print(np.average(score))


