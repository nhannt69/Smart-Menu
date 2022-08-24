import os
import pandas as pd
import json


class Metric():

    def readFile(self):
        result = pd.read_excel('data_sample\Data_Labeling.xlsx',  header=None)
        return result
  
    def evaluation(self, result):
    
        dataframe = self.readFile()
        dataframe_image = dataframe[dataframe[0] == result[0]]

        print(dataframe_image)
        
        score = 0.0

        prediction, recall, f1_score = 0.0, 0.0, 0.0
        tp_count = 0
        tn_count = 0

        prediction_translate, recall_translate, f1_score_translate = 0.0, 0.0, 0.0
        tp_count_translate = 0
        tn_count_translate = 0

        for obj in result[1::]:
            dataframe_namevi = None
            print(obj[0])
            dataframe_namevi = dataframe_image[dataframe_image[1] == obj[0].upper()]

            # print(dataframe_namevi)
            
            dataframe_price = dataframe_namevi[dataframe_namevi[3] == obj[1]]

            print(dataframe_price)

            dataframe_nameen = dataframe_namevi[dataframe_namevi[2] == obj[2]]
            
            if (dataframe_price.empty):
                tn_count += 1
            else:
                tp_count += 1
            
            if (dataframe_nameen.empty):
                tn_count_translate += 1
            else:
                tp_count_translate += 1
        
        #prediction
        print(tp_count, tn_count)
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
            print(prediction, recall)
        except:
            pass
        try:
            f1_score_translate = 2.0*(prediction_translate * recall_translate)/(prediction_translate + recall_translate)
        except:
            pass

        score =   0.9*f1_score + 0.1*f1_score_translate

        return score, f1_score, f1_score_translate

        

if __name__ == "__main__":
    menu = ['002.jpeg',('Rau muống xào tỏi', '29000', 'SAUTEED WATER SPINACH WITH GARLIC'),('Cải xào tỏi', '29000', 'SAUTEED BORECOLE WITH GARLIC'),('Đậu xào', '145800', 'SAUTEED BORECOLE WITH GARLIC'),('Gà nướng', '45000', 'Chicken')]
            
    evaluation = Metric()
    
    print(evaluation.evaluation(result= menu))
    

    # print(dataframe_image)
                 