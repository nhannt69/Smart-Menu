import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
sys.path.insert(1, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\postprocessing')
sys.path.insert(2, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\ocr')
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import numpy as np
import pandas as pd
import time
import argparse

from ocr.tools.config import Cfg
from ocr.OCR import Reader
import postprocessing.mapping
from postprocessing.post_preprocess import PostPreprocessor
from translate.translate import Translator_Menu
from test_evaluation.test_evaluation_tuple import Metric

class Extractor:
  def __init__(self):
    #load config sử dụng cho ocr
    config = Cfg.load_config_from_file('.\ocr\config\\vgg-transformer.yml')
    self.reader = Reader(config, gpu=False)

    #postprocessing
    self.postprocessing = PostPreprocessor(debug=False)
    #translate
    self.translate = Translator_Menu()

  
  def extract_menu(self, input, image_name):    
    ## Detect + OCR ##
    image_path = input
    result = list(self.reader.readtext(image_path, image_name=image_name))
    
    ## Post processing ##
    result_map = self.postprocessing.preprocess(result)

    ## Translate ##
    pairs = []
    pairs.append(image_name)
    pairs = self.translate.process_translate(result_map)

    return pairs

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--input_file", help="input file path")
  parser.add_argument("--input_folder", help="input folder path")
  args = parser.parse_args()
  metric = Metric()
  list_score = []

  extract = Extractor()
  time_st = time.time()
  for file in os.listdir(args.input_folder):
    file_path = os.path.join(args.input_folder, file)

    start_time = time.time()
    pairs = extract.extract_menu(file_path, file_path[-8::])
    score, f1_ocr, f1_trans = metric.evaluation(pairs)
    list_score += [score]
    with open("result.txt", "a") as f:
      f.write(f'\n{file_path[-8::]}: {score, f1_ocr, f1_trans}')
    print(f'Elapsed time: {time.time() - start_time}')
  print(np.average(list_score))
  time_fi = time.time() - time_st
  print(time_fi)


