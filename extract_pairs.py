import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
sys.path.insert(1, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\postprocessing')
sys.path.insert(2, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\ocr')
from email import header
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from googletrans import Translator
import cv2
import re
from fuzzywuzzy import process
import numpy as np
import time
import argparse
from PIL import Image
import io
import random
import datetime
import string
from ocr.tools.config import Cfg
from ocr.OCR import Reader
from postprocessing.dictionary_menu import Formating_Dictionary
import pandas as pd

class Extractor:
  def __init__(self, referenced_translations='data_sample\Data_Labeling.xlsx'):
    config = Cfg.load_config_from_file('.\ocr\config\\vgg-transformer.yml')
    self.reader = Reader(config, gpu=False)
    # self.reader = easy_reader
    self.format_result = Formating_Dictionary('postprocessing\dictionary_menu.xlsx')
    self.translator = Translator()
    self.referenced_translations = {}
    if referenced_translations:
      labels_df = pd.read_excel(referenced_translations, header= None)
      for index, row in labels_df.iterrows():
          self.referenced_translations[row[1]] = row[2]

  def draw_bbs(self, image, horizontal_list):
    color = (255, 0, 0) 
    thickness = 2

    for box in horizontal_list[0]:
      image = cv2.rectangle(image, (box[0], box[2]), (box[1], box[3]), color, thickness) 
    
    return image
  
  def in_one_line(self, coor_1, coor_2):
    """
    [([[348, 272], [548, 272], [548, 300], [348, 300]], 'Bánh hỏi heo quay', 0.716558878485797), ([[581, 275], [667, 275], [667, 295], [581, 295]], '40.oo0đ', 0.5197626695252079)],
    """
    coor_1_y_min = coor_1[0][1] #272
    coor_1_y_max = coor_1[2][1] #300
    coor_2_y_min = coor_2[0][1] #275
    coor_2_y_max = coor_2[2][1] #295
    coor_2_y_center = (coor_2_y_min + coor_2_y_max)/2 # (275 + 295)/2 = 570/2 = 285
    if coor_2_y_center > coor_1_y_min and coor_2_y_center < coor_1_y_max: #285>272 and 285 < 300
      return True
    return False
  
  def extract_lines(self, result):
    patient = 2
    lines = []
    boxes = [box[0] for box in result]
    # print(boxes)
    i = 0
    while i < len(boxes):
      line = [result[i]]
      first_box_id = i
      try:
        while i+1 < len(boxes) and self.in_one_line(boxes[first_box_id], boxes[i+1]):
          line.append(result[i+1])
          # print('======================')
          # print(line)
          i += 1
      except Exception as e:
        print(f'Exception {e}')

      lines.append(line)
      i += 1
    # print(lines)
    return lines
  
  def filename_gen(self):
    basename = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    return "".join([basename, suffix])+".jpg"  # e.g. 'mylogfile_120508_171442'

  def post_process(self, price):
    if price == 'miễnphí':
      return 'Free'
    else:
      if len(price) < 4:
        return price + '000'
      return price

  def extract_menu(self, input):
    if isinstance(input, str):
      ## Detect + OCR ##
      image_path = input
      # image = cv2.imread(image_path)
      result = list(self.reader.readtext(image_path))
      # print(f' 1 2 3 {result}')
      
      ## Extract lines ##
      lines = self.extract_lines(result)

    elif isinstance(input, list):
      lines = input
    
    elif isinstance(input, bytes):
      result = list(self.reader.readtext(input))
      
      ## Extract lines ##
      lines = self.extract_lines(result)



    ## Extract pairs ##
    time_postprocessing = time.time()
    pairs = []
    # price_pattern = r"(\d{1,3}k(\/\w{1,3})?)|((\d\s?){1,3}[\.\,](\d\s?){3}\s?(d|đ|vnđ|vnd)?)|miễn\sphí"
    price_pattern = r"(\d{2,3}k?)|((\d\s?){[1,3}\.\,](\d\s?){3}\s?)|miễn\sphí" #Hỏi quân ??? regular expression 300k 3000k 15000 (\d{2,3}k?) 1     k

    '''
    Referenced Translations Structure:

    referenced_translations = {
      'vi_1': 'en_1',
      'vi_2': 'en_2'
    }

    '''
    referenced_names = list(self.referenced_translations.keys())

    for line in lines:
      i = 0
      try:
        while True:
          food_name = line[i][1]
          # print(re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0')))
          while not (re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0')) or re.match(price_pattern, line[i+1][1].lower().replace('O','0').replace('o','0'))):
            food_name += ' ' + line[i+1][1]
            # print(food_name)
            i += 1
            if i + 1 >= len(line):
              break

          if re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0')):
            price = re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0'))
            # print(f'case 1: price = {price}')
            # print(f'foodname: foodname = {food_name[:-len(price.group())]}')
            food_name = food_name[:-len(price.group())]
            # print('CASE 2')
            # print(food_name)
          else:
            if i + 1 >= len(line):
              break
            price = re.match(price_pattern, line[i+1][1].lower().replace('O','0').replace('o','0'))
            # print(f'case 2: price = {price}')
            # print(f'foodname: foodname = {food_name}')
            
          if price:
            price = price.group().replace(' ', '').replace('.', '').replace('k', '000').replace('O','0').replace('o','0')
            price = self.post_process(price)
            # print(f'case 3: price = {price}')
            # print(f'foodname: foodname = {food_name}')

            time_postprocessing_finish = time.time() - time_postprocessing

            time_translate = time.time()
            # ## Translation ##
            translated_name = ''

            best_match = process.extractOne(food_name, referenced_names) #file image -> food_name #change dataset and unique data sample about food_name
            # print('best_match')
            # break
            if best_match and best_match[1] >= 90:
              try:
                translated_name = self.referenced_translations[best_match[0]].strip()
                print(f'Into list {translated_name}')
              except:
                translated_name = ''
              
            if translated_name == '':
              translation = self.translator.translate(food_name, dest='en', src='vi')
              translated_name = translation.text
              print(f'googe translate {translated_name}')
              pass
            time_translate_finish = time.time() - time_translate
                      
          if price[0] != '0':
            pairs.append((self.format_result.format_result_dict(food_name.upper()), price, translated_name))
            # print(food_name)
          i += 2
      except Exception as E:
        print(f'Exception: {E}')
        pass
    with open("postprocessing\post_text_time.txt", "a") as f:
      f.write(f"\n===========Post Pre=============\n{str(time_postprocessing_finish)}\ntime-transalte: {str(time_translate_finish)}")

    return pairs

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--input_file", help="input file path")
  parser.add_argument("--input_folder", help="input folder path")
  args = parser.parse_args()

  
  labels_df = pd.read_excel('data_sample\Data_Labeling.xlsx', header = None)
  print(labels_df)
  referenced_translations = {}
  for index, row in labels_df.iterrows():
      referenced_translations[row[1]] = row[2]
      # print(referenced_translations)

  extractor = Extractor('data_sample\Data_Labeling.xlsx')
  start_time = time.time()
  pairs = extractor.extract_menu(args.input_file)
  # print(type(pairs))
  # print(f'{args.input_folder}/{pairs["image_name"]}_ocr.txt')
  # with open(f'{args.input_folder}/{pairs[0]["image_name"]}_ocr.txt', 'w', encoding='utf8') as f:
  #   f.write(f'{pairs}')
  print(pairs)
  print(f'Elapsed time: {time.time() - start_time}')