import codecs
import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
sys.path.insert(1, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\postprocessing')
sys.path.insert(2, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\ocr')
from email import header
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
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

class PostProcessing():
  def __init__(self):
    #postprocessing
    self.format_result = Formating_Dictionary('postprocessing\dictionary_menu.xlsx')
  
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
        """
        Input: result
        output: line 
        """
        time_extractline = time.time()
        lines = []
        #tạo list boxes chứa các box đã được trả về từ kết quả ocr
        boxes = [box[0] for box in result]
        #tạo vòng lặp để duyệt từng box để xem nếu lần lượt hai box thỏa mãn sẽ có thể đưa vào list line -> hai box cùng dòng
        i = 0
        while i < len(boxes):
            line = [result[i]]
            first_box_id = i
            try:
                # do thứ tự box có thể xáo trộn nên ta dùng vòng lặp thứ hai để tìm xem có box nào thỏa mãn điều kiện với box trước đó.
                # hàm in_one_line sẽ trả về True nếu tọa độ hai box thỏa điều kiện
                while i+1 < len(boxes) and self.in_one_line(boxes[first_box_id], boxes[i+1]):
                #thỏa điều kiện thì gom hai box vào list line
                    line.append(result[i+1])
                    i += 1
            except Exception as e:
                print(f'Exception {e}')
            #sort with x[0]
            def get_index(list_child):
                return list_child[0][0]
            line.sort(key=get_index)
            lines.append(line)
            i += 1
        time_finish_exline = time.time() - time_extractline
        return lines, time_extractline

  def reformat(self, price):
    if price == 'miễnphí':
      return 'Free'
    else:
      if len(price) < 4:
        return price + '000'
      return price

  def extract_menu(self, result):    
    ## Extract lines ##
    lines, time_extractline = self.extract_lines(result)
    # print(time_extractline)

    ## Extract pairs ##
    pairs = []
    
    price_pattern = r"(\d{2,3}k?)|((\d\s?){[1,3}\.\,](\d\s?){3}\s?)|miễn\sphí" 

    for line in lines:
      i = 0
      try:
        while True:
          #Lấy giá trị tên món và giá đối với line
          food_name = line[i][1]
          #kiểm tra xem nó có giống dạng giá - pattern không hoặc kiểm tra xem line tiếp theo có giống dạng giá không
          # mục đích là có thể hai box chứa hai cụm từ và hai cụm từ này là một món ăn
          while not (re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0')) or re.match(price_pattern, line[i+1][1].lower().replace('O','0').replace('o','0'))):
            food_name += ' ' + line[i+1][1]
            i += 1
            if i + 1 >= len(line):
              break
          # kiểm tra chuỗi food_name có là giá không để thay đổi thành price
          if re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0')):
            #lấy ra vị trí đầu tiên giống nhau khi giống pattern
            price = re.search(price_pattern, food_name.lower().replace('O','0').replace('o','0'))
            #trường hợp món ăn và giá có thể liền nhau, foodname= 'gà200k', khi so pattern thì thấy có 200k nên TRUE -> có chứa giá -> lấy giá
            #nếu lấy price = food_name thì có thể không đảm bảo vì trong chuỗi food_name không hẳn 100% là giá. Do đó ngược các ký tự theo công thức -<kích thước price>
            food_name = food_name[:-len(price.group())]

          else:
            if i + 1 >= len(line):
              break
            # vì để mặc định phần tử là tên món, do đó nếu trường hợp tại dòng đó không phải thì xem như là giá
            # food_name không phải giá thì kiểm tra dòng tiếp theo có phải là giá không
            price = re.match(price_pattern, line[i+1][1].lower().replace('O','0').replace('o','0'))
            
          if price:
            price = price.group().replace(' ', '').replace('.', '').replace('k', '000').replace('O','0').replace('o','0')
            price = self.reformat(price)
            
          if price[0] != '0':
            pairs.extend([self.format_result.format_result_dict(food_name.upper()), price])

          i += 2
      except Exception as E:
        # print(f'Exception: {E}')
        pass
    # with open("postprocessing\post_text_time.txt", "a") as f:
    #   f.write(f"\n===========Post Pre=============\n{str(time_postprocessing_finish)}\ntime-transalte: {str(time_translate_finish)}")

    return pairs

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="input file path")
    parser.add_argument("--input_folder", help="input folder path")
    args = parser.parse_args()

    time_loadConfig = time.time()
    reader = Reader(config = Cfg.load_config_from_file('.\ocr\config\\vgg-transformer.yml'))
    post_pro = PostProcessing()
    time_loadConfig_finish = time.time() - time_loadConfig

    for file in os.listdir(args.input_folder):
        file_path = os.path.join(args.input_folder, file)

        time_start = time.time()
        result_ocr = list(reader.readtext(file_path, file_path))
        time_ocr_finish = time.time() - time_start

        time_start_post = time.time()
        pairs = post_pro.extract_menu(result_ocr)
        time_finish_post = time.time() - time_start_post

        time_all = time.time() - time_start

        with open("postprocessing\post_text_time.txt", "a") as f:
            f.write(f"\n{file_path}: Time load config: {time_loadConfig_finish} Time OCR: {time_ocr_finish} Time Postprocessing {time_finish_post} Time {time_all}")
        f = codecs.open("postprocessing\\result_postprocessing.txt", "a", 'utf8')
        f.write(f'{pairs}\n')
        
        print(pairs)