"""
File txt contain this generally result ocr
"""
import argparse
import numpy as np
import os
import pandas as pd

def readFile():
    result = pd.read_excel('data_sample/Data_Labeling.xlsx',  header=None)
    return result

def processing_data(list_string):
    list_item = list()
    list_item = [[item.upper(), '169000'] for item in list_string]
    return list_item

def convert_to_list(file_test_path, index):
    """
    convert string to list
    """
    list_string = pd.read_table(file_test_path, header= None)
    result_list = list_string.loc[index, 2]
    result_list_change = result_list.replace("', '", "  ").replace("']", "").replace("['", "")
    list_change = list(result_list_change.split("  "))
    return list_change

if __name__ == "__main__":
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
    parser.add_argument("-i", "--file_path", help="file txt contains results ocr")
    args = parser.parse_args()

    score = list()

    test_path = args.file_path

    list_string = pd.read_table(test_path, header= None)

    
    for index in range(list_string.shape[0]):


        list_string = convert_to_list(test_path, index)

        
        image_file = list_string[0]

        result_ocr = processing_data(list_string)
        
        print(data_sample[data_sample[0].isin([image_file])])

        data_filter = data_sample[data_sample[0].isin([image_file])]

        prediction, recall, f1_score = 0.0, 0.0, 0.0
        tp_count = 0
        tn_count = 0
        for item_ocr in result_ocr:
            data_filter_food = data_filter[data_filter[1].isin([item_ocr[0]])]
            if data_filter_food is not None:
                data_filter_price = data_filter_food[data_filter_food[3].isin([item_ocr[1]])]

                if data_filter_food.empty: #giả sử chưa quan tâm đến giá
                    tn_count += 1
                else:
                    tp_count += 1
                    print(data_filter_food)
        #prediction
        try:
            prediction = 1.0*tp_count/(tp_count + tn_count)
        except:
            prediction = 0.0
        #recall
        fn_count = data_filter.shape[0] - tp_count
        try:
            recall = 1.0*tp_count/(tp_count + fn_count)
        except:
            recall = 0.0
        #f1 score
        try:
            f1_score = 2.0*(prediction * recall)/(prediction + recall)
        except:
            f1_score = 0.0
        score += [f1_score]

        print(f'prediction {prediction}')
        print(f'recall {recall}')
        print(f'f1_score {f1_score}')
        print(score)
        print("=====================================================================")

    print(score)
    print(np.average(score))


