from ocr.tools.translate import process_image
from tools.translate import build_model, translate, translate_beam_search, process_input, predict
import torch
from PIL import Image
import cv2
import pytesseract
import numpy as np
from preprocessing import preprocessing

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\\tesseract'

class Predictor():
    def __init__(self, config): #__init__(self, config)

        device = config['device']
        
        model, vocab = build_model(config)
        weights = 'ocr/weights/transformerocr.pth'

        model.load_state_dict(torch.load(weights, map_location=torch.device(device)))

        self.config = config
        self.model = model
        self.vocab = vocab
        

    def predict(self, img):
        import time
        time_finish = 0
        time_start = time.time()
        img = process_input(img, self.config['dataset']['image_height'], 
                self.config['dataset']['image_min_width'], self.config['dataset']['image_max_width'])   

        img = img.to(self.config['device'])

        if self.config['predictor']['beamsearch']:
            sent = translate_beam_search(img, self.model)
            s = sent
        else:
            sents = translate(img, self.model)
            s = translate(img, self.model)[0].tolist()

        s = self.vocab.decode(s)
        # custom_config = r'-l vie --oem 1 --psm 6'

        # # now feeding image to tesseract
       
        # s = pytesseract.image_to_string(img, config=custom_config).strip()

        time_finish = time.time()-time_start

        return s, time_finish


def get_text(recognizer,image_list):
    coord = [item[0] for item in image_list]
    img_list = [item[1] for item in image_list]
    result_str = []
    list_time= []
    for img in img_list:
        result, time_finish = recognizer.predict(img)
        result_str.append(result)
        list_time += [time_finish]
        # import codecs
        # f = codecs.open("postprocessing\\post_processing_result\\result_ocr.txt", "a", "utf8")
        # f.write(f'\n{result_str}\n{list_time}')
        
    result = []

    for box, rs in zip(coord, result_str):
        result.append([box, rs])
    return result