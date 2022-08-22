import codecs
from ntpath import join
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import sys
sys.path.insert(0, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master')
sys.path.insert(1, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\ocr')
sys.path.insert(1, 'C:\chuyen\\fpt-software\.test\OCR-Vietnamese-master\OCR-Vietnamese-master\postprocessing')
from detection import get_detector, get_textbox
from recognition import Predictor, get_text
from utils import group_text_box, get_image_list,printProgressBar,reformat_input,diff, loadImage
# from bidi.algorithm import get_display
import numpy as np
import cv2
import torch
import os
import sys
from PIL import Image
from logging import getLogger
import time
from urllib.request import urlretrieve
from pathlib import Path
from tools.config import Cfg
import argparse
from preprocessing.preprocessing import preprocessing_menu
class Reader(object):

    def __init__(self, config, gpu=True, model_storage_directory=None,
                 download_enabled=True, detector=True, recognizer=True):
        time_load_model = time.time()
        self.config = config
        
        self.device = config['device']

        self.detector_path = config['detection']['model_path']
        if detector:
            self.detector = get_detector(self.detector_path, self.device)
        if recognizer:
            self.recognizer = Predictor(config)
        self.time_load_config = time.time() - time_load_model

    def detect(self, img, min_size = 20, text_threshold = 0.7, low_text = 0.4,\
               link_threshold = 0.4,canvas_size = 2560, mag_ratio = 1.,\
               slope_ths = 0.1, ycenter_ths = 0.5, height_ths = 0.5,\
               width_ths = 0.5, add_margin = 0.1, reformat=True):

        if reformat:
            img, img_cv_grey = reformat_input(img)

        text_box = get_textbox(self.detector, img, canvas_size, mag_ratio,text_threshold, link_threshold, low_text,False, self.device)
        horizontal_list, free_list = group_text_box(text_box, slope_ths,ycenter_ths, height_ths,width_ths, add_margin)
        
        if min_size:
            horizontal_list = [i for i in horizontal_list if max(i[1]-i[0],i[3]-i[2]) > min_size]
            free_list = [i for i in free_list if max(diff([c[0] for c in i]), diff([c[1] for c in i]))>min_size]

        return horizontal_list, free_list
    
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
  
    def extract_lines_sorted(self, result):
            """
            Input: result
            output: line 
            """
            lines = []
            result_change = []
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
                for item in line:
                    result_change.append(item[1])
                i += 1

            return result_change


    def recognize(self, img, image_name, horizontal_list=None, free_list=None,reformat=True,imgH = 32):

        if reformat:
            img, img_cv_grey = reformat_input(img)

        if (horizontal_list==None) and (free_list==None):
            b,y_max, x_max = img.shape
            ratio = x_max/y_max
            max_width = int(imgH*ratio)
            crop_img = cv2.resize(img, (max_width, imgH), interpolation =  Image.ANTIALIAS)
            image_list = [([[0,0],[x_max,0],[x_max,y_max],[0,y_max]] ,crop_img)]
            
        else:
            image_list, max_width = get_image_list(horizontal_list, free_list, img, model_height = imgH)

        result = get_text(self.recognizer,image_list)

        result_change_sorted = self.extract_lines_sorted(result= result)

        print(result_change_sorted)

        result_change_sorted.insert(0, str(image_name[-8:]))
       
        f = codecs.open(f"ocr\ocr_results\detect_recognize\\result_ocr_sorted.txt", "a+", encoding='utf8')
        f.write(f"\n{result_change_sorted}")
        return result_change_sorted

    def readtext(self, image, image_name, min_size = 20,\
                 text_threshold = 0.7, low_text = 0.4, link_threshold = 0.4,\
                 canvas_size = 2560, mag_ratio = 1.,\
                 slope_ths = 0.1, ycenter_ths = 0.5, height_ths = 0.5,\
                 width_ths = 0.5, add_margin = 0.1):
        '''
        Parameters:
        image: file path or numpy-array or a byte stream object
        '''
        img, img_cv_grey = reformat_input(image)

        # time_detect = time.time()

        horizontal_list, free_list = self.detect(img, min_size, text_threshold,\
                                                 low_text, link_threshold,\
                                                 canvas_size, mag_ratio,\
                                                 slope_ths, ycenter_ths,\
                                                 height_ths,width_ths,\
                                                 add_margin, False)
        # time_detect_finish = time.time() - time_detect

        #==========================================
        # try:
        #     img_copy = loadImage(image)
        #     for list_box in horizontal_list:
        #         cv2.rectangle(img_copy, (list_box[0], list_box[2]), (list_box[1], list_box[3]), (0,0,255), 1)
        #     bar = '\\'
        #     bar_2 = '/'
        #     try:
        #         cv2.imwrite(f"ocr\image_detect\img_detect1_{str(image_name).split(bar)[-1]}", img_copy)
        #     except:
        #         pass
            
        #     try:
        #         cv2.imwrite(f"ocr\image_detect\img_detect1_{str(image_name).split(bar_2)[-1]}", img_copy)
        #     except:
        #         pass
        # except:
        #     pass
        
        #==========================================      
        # time_recognize = time.time()
        result = self.recognize(img, image_name, horizontal_list, free_list,False)
        # time_recognize_finish = time.time() - time_recognize

        # with open("test/result_info1.txt", "a+") as f:
        #     f.write(f'\n\n{image_name}\ntime load config: {self.time_load_config}\ntime detect ocr: {time_detect_finish}\ntime recognize ocr: {time_recognize_finish}')
        return result
if __name__ == '__main__':
    config = Cfg.load_config_from_file('ocr\config\\vgg-transformer.yml')
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_path", help="path to image test")
    args = parser.parse_args()

    
    reader = Reader(config)

    for file in os.listdir(args.folder_path):
        start = time.time()
        image_path = os.path.join(args.folder_path, file)
        result = reader.readtext(preprocessing_menu(image_path), image_name= image_path)
        if (result):
            print(True)
        else:
            print(False)
        print(time.time()-start)

    