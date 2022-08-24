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
    pairs = self.translate.process_translate(result_map)

    return pairs

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--input_file", help="input file path")
  parser.add_argument("--input_folder", help="input folder path")
  args = parser.parse_args()

  extract = Extractor()
  result = extract.extract_menu(args.input_file, args.input_file[-8::])

  print(result)


