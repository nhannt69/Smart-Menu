import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
from test_evaluation.test_metric import Metric
import requests
import base64
import os,json,sys
import base64
import argparse
import os
import numpy as np

class Request():

    def __init__(self, folder_path):
        self.file_path = folder_path

    def count_file(self):
        _, _, files = next(os.walk(self.folder_path))
        file_count = len(files)
        return file_count

    def request_image(self, img_path):

        score = 0.0

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }

        
        with open(img_path, "rb") as image_file:
            data = base64.b64encode(image_file.read())

        image_name= os.path.basename(img_path)
        response = requests.post(
            url='http://localhost:5000/infer',
            data={
                "image": data,
                "image_name": image_name
            }
            , headers=headers
        )

        ## Print output
        if response.status_code == 200:
            print(response.json())

        #kết quả 
        result = response.json()

        evaluation = Metric()
        
        score = evaluation.evaluation(result)
        return score

    def request_folder(self):
        score_list = []
        score_arg = 0.0
        for img in os.listdir(self.file_path):
            img_path = os.path.join(self.file_path, img)
            score = self.request_image(img_path= img_path)
            score_list += [score]
        score_arg = np.average(score)
        return score_list, score_arg



if __name__ == "__main__":

        parser = argparse.ArgumentParser()
        parser.add_argument("--input_folder", help="Input folder contain image input")
        args = parser.parse_args()

        request_api = Request(args.input_folder)

        score_list = []
        score_arg = 0.0

        score_list, score_arg = request_api.request_folder()

        print(score_arg, score_list)

        

        