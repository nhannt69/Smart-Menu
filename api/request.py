import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
from test_evaluation.test_metric import Metric
import requests
import base64
import os,json,sys
import base64
import argparse




test_link = "http://0.0.0.0:5000/infer"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

parser = argparse.ArgumentParser()
parser.add_argument("--input_file", help="input file path")
parser.add_argument("--input_folder", help="input folder path")
args = parser.parse_args()

img_path = args.input_file

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

# print(str(result))

evaluation = Metric()
s, f1, f1_trans = evaluation.evaluation(result)

# with open(f'{args.input_folder}/{result["image_name"]}_ocr.txt', 'w', encoding='utf8') as f:
#   f.write(f'{result}')