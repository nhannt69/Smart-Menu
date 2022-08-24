
import ast
import logging

import mapping
from post_preprocess import PostPreprocessor

if __name__ == '__main__':

    post_preprocessor = PostPreprocessor(debug = True)

    with open('postprocessing/ocr_entities_testcases.txt', 'r', encoding='utf-8') as f:
        for line in f:
            test_case = ast.literal_eval(line)

            img = test_case[0]
            test_case = test_case[1:]
            post_preprocessor.logger.log(logging.DEBUG, f"Image {img}")

            post_preprocessor.preprocess(test_case)


            # test = "COMBO ĐỒNG GIÁ 169K BÚN ĐẬU GÁNH ĐẶC BIỆT 79.000 NEM CHUA NEM CHUA 55,000 55,000"
            # print(mapping.clean_raw_text(test))

            #break

