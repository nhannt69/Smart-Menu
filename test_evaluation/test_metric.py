import os
import pandas as pd
import json


class Metric():

    def readFile(self):
        result = pd.read_excel('data_sample\Data_Labeling.xlsx',  header=None)
        return result
  
    def evaluation(self, result):
    
        dataframe = self.readFile()
        dataframe_image = dataframe[dataframe[0] == result['image_name']]

        result_ocr = result['infers']

        score = 0.0

        prediction, recall, f1_score = 0.0, 0.0, 0.0
        tp_count = 0
        tn_count = 0

        prediction_translate, recall_translate, f1_score_translate = 0.0, 0.0, 0.0
        tp_count_translate = 0
        tn_count_translate = 0

        for obj in result_ocr:
            dataframe_namevi = None
            
            dataframe_namevi = dataframe_image[dataframe_image[1] == obj["food_name_vi"]]
            
            dataframe_price = dataframe_namevi[dataframe_namevi[3] == obj["food_price"]]

            dataframe_nameen = dataframe_namevi[dataframe_namevi[2] == obj["food_name_en"]]
            
            if (dataframe_price.empty):
                tn_count += 1
            else:
                tp_count += 1
            
            if (dataframe_nameen.empty):
                tn_count_translate += 1
            else:
                tp_count_translate += 1
        
        #prediction
        try:
            prediction = 1.0*tp_count/(tp_count + tn_count)
            prediction_translate = 1.0*tp_count_translate/(tp_count_translate + tn_count_translate)
        except:
            prediction = 0.0
            prediction_translate = 0.0
        #recall
        fn_count = dataframe_image.shape[0] - tp_count
        fn_count_translate = dataframe_image.shape[0] - tp_count_translate
        try:
            recall = 1.0*tp_count/(tp_count + fn_count)
            recall_translate = 1.0*tp_count_translate/(tp_count_translate + fn_count_translate)
        except:
            recall = 0.0
            recall_translate = 0.0
        
        #f1 score
        try:
            f1_score = 2.0*(prediction * recall)/(prediction + recall)  
        except:
            pass
        try:
            f1_score_translate = 2.0*(prediction_translate * recall_translate)/(prediction_translate + recall_translate)
        except:
            pass

        score =   0.9*f1_score + 0.1*f1_score_translate

        return score, f1_score, f1_score_translate

        

if __name__ == "__main__":
    result = {'image_name': '002.jpeg', 'infers': [{'food_name_en': 'Opening time 13h', 'food_name_vi': 'THỊT RANG CHÁY CẠNH', 'food_price': '13000'}, \
        {'food_name_en': 'STIR-FRIED KANGKONG WITH GARLICS', 'food_name_vi': 'RAU MUỐNG XÀO TỎI', 'food_price': '29000'}, \
            {'food_name_en': 'FRIED MALABAR SPINACH WITH GARLIC', 'food_name_vi': 'MỒNG TƠI XÀO TỎI', 'food_price': '29000'}]}

            
    evaluation = Metric()
    
    evaluation.evaluation(result= result)
    

    # print(dataframe_image)
                 