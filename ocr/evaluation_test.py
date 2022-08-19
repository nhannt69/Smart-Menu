"""
File txt contain this generally result ocr
"""
import argparse
from typing import overload
import numpy as np
import os
import pandas as pd
import re


FILE_PATH = 'data_sample\Data_Labeling.xlsx'

class EvaluationMetricOCR():
    def __init__(self, file_path):
        self.file_path = file_path

    def read_data(self, file_path_result):
        #load file result
        file_result = pd.read_table(file_path_result, header= None)
        return file_result

    def procesing_image_name(self, image_name: str):
        """
        image name be formatted to correctly format
        """
        image_name_new = image_name.replace("'],", "").replace("']", "").replace("\"\'", "")[1::]
        return image_name_new

    def convert_to_list(self, dataframe_line):
        """
        Input: "[[(),(), (), '<str?>']"
        Output: [(), (), (), <str?>]
        """
        # đưa về dạng [[] -> [] or []] -> []
        dataframe_line_new = str(dataframe_line).replace("[[", "[").replace("]]", "]").replace("), (", "),  ("). replace("[(", "(").replace("'), '", "'),  '") #xử lý dỏng cuối để cho ảnh thành 1 chuối
        #ngắt chuỗi để biến đổi về list
        dataframe_line_split = list(dataframe_line_new.split(",  "))

        return dataframe_line_split
    
    def convert_to_list_child(self, child_line:str):
        """
        Input: "([], <str>)"
        Output: [[], [<str>]]
        """
        #đưa về dạng ()-> mất
        child_line_new = child_line.replace(", '", ",  '").replace("(", "").replace(")", "").replace(",  '", ",  ").replace("\'", "")
        child_line_list = list(child_line_new.split(",  "))

        return child_line_list

    def isPrice(self, child_list_element):
        flag = False
        price_pattern = r"(\d{2,3}k?)|((\d\s?){[1,3}\.\,](\d\s?){3}\s?)|miễn\sphí"
        #sử dụng regular expression
        if re.search(price_pattern, child_list_element.lower().replace('O','0').replace('o','0')) != None:
            flag = True
        return flag

    def post_process(self, price):
        price = str(price).replace(' ', '').replace('.', '').replace('k', '000').replace('O','0').replace('o','0')
        if price == 'miễnphí':
            return 'Free'
        else:
            if len(price) < 4:
                return price + '000'
            elif ("/" in price):
                return price.split("/")[0]
            return price

    def compute_metric(self, file_path_result):
        #load data sample
        dataframe = pd.read_excel(self.file_path)
        data_result = self.read_data(file_path_result)
        percentage_list = []

        #theo từng ảnh
        for index in range(data_result.shape[0]):
            #khai báo lại các giá trị cho từng ảnh
            percentage, count, count_wrong = 0, 0, 0
            dataframe_filter_line = data_result.loc[index, 0]
            dataframe_filter_line_list = self.convert_to_list(dataframe_line= dataframe_filter_line)

            image_file = self.procesing_image_name(dataframe_filter_line_list.pop())

            #load sample data compare with image name into data labelling file
            dataframe_child = dataframe[dataframe['ImageName'] == image_file]
            print(dataframe_child)
            sum_count = dataframe_child.shape[0]

            for index in range(len(dataframe_filter_line_list)):
                #khai báo lại cho dataframe_food
                dataframe_child_filter_food = pd.DataFrame()
                child_list = self.convert_to_list_child(dataframe_filter_line_list[index])
                #lấy các dòng có thông tin giá và món ăn tiếng Việt trùng với khi trích xuất
                if (self.isPrice(child_list[-1])):
                    price = self.post_process(child_list[-1])
                else:
                    dataframe_child_filter_food = dataframe_child[dataframe_child['VietnameseName'] == child_list[-1].upper()]
                
                if dataframe_child_filter_food.empty:
                    count_wrong += 1
                else:
                    count += 1
            try:
                percentage = (count/sum_count)
            except Exception as e:
                print(e)
                pass
            print(percentage)
            percentage_list += [percentage]
            with open("ocr\ocr_results\\result_OCR_gray_1_108.txt", "a") as f:
                f.write(f'\nImage name: {image_file} - Result: {percentage}')
        print(percentage_list)
        print(np.average(percentage_list))                    
                
                
               
            

        return True

 

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", help= "file contain result ocr")
    args = parser.parse_args()

    file_path_result = args.file_path

    evaluation_metric = EvaluationMetricOCR(file_path= FILE_PATH)

    evaluation_metric.compute_metric(file_path_result)

    

    
    





