import ast
import logging
import os
import re
import sys

sys.path.insert(0, f"{os.path.dirname(__file__)}/..")

import numpy as np
from test_evaluation.test_evaluation_tuple import Metric

import mapping
from post_preprocess import PostPreprocessor
from spellchecker import SpellChecker

if __name__ == "__main__":

    post_preprocessor = PostPreprocessor(debug=True)

    #print(post_preprocessor.spellchecker.correct_spell('rau muốn xào', 'hành'))
    metric = Metric()
    scores = []
    with open("postprocessing/ocr_entities_testcases.txt", "r", encoding="utf-8") as f:
        for line in f:
            test_case = ast.literal_eval(line)

            img = test_case[0]
            test_case = test_case[1:]
            post_preprocessor.logger.log(logging.DEBUG, f"Image {img}")

            output = post_preprocessor.preprocess(test_case)

            output = [(food.upper(), price, 'None') for food, price in output]

            #output.insert(0, img)



            f1_score = metric.evaluation(output, img)[1]
            scores.append(f1_score)
            post_preprocessor.logger.info(f"Score: {f1_score}\n" + "-"*50)



            # test = "COMBO ĐỒNG GIÁ 169K BÚN ĐẬU GÁNH ĐẶC BIỆT S: 39K L: 79K"
            # print(mapping.clean_raw_text(test))

            # break

    avg_score = np.mean(scores)
    post_preprocessor.logger.info(f"\n\nAverage Score: {avg_score}")
