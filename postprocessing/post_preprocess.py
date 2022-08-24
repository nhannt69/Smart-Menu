
import logging
import os
from datetime import date
from typing import List

import mapping
from spellchecker import SpellChecker


class PostPreprocessor(object):
    def __init__(self, debug=False):

        folder_path = os.path.dirname(__file__)

        self.spellchecker = SpellChecker(f'{folder_path}/food_vocabulary/one_gram.txt', f'{folder_path}/food_vocabulary/big_gram.txt')

        self.logger = self.__init__logger(debug)


    def __init__logger(self, debug):
        logger = logging.getLogger(__name__)
        fh = logging.FileHandler(f"{os.path.dirname(__file__)}/test_log/post_results_{date.today()}.log", mode = 'a', encoding = 'utf-8')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
        fh.setFormatter(f_format)

        log_level = logging.DEBUG if debug else logging.INFO

        fh.setLevel(log_level)
        logger.setLevel(log_level)

        logger.addHandler(fh)

        return logger


    def preprocess(self, entities:List[str]):
        #Clean text
        text = "\n".join(entities)
        text = mapping.clean_raw_text(text)
        entities = text.split('\n')

        #Step 1: Classify food and prices
        foods, prices = mapping.get_price_and_food(entities)

        self.logger.log(logging.DEBUG, f"Step 1 classify: \nFOODS: {foods}\nPRICES: {prices}")

        #Step 2: Correct spell for foo entities
        foods = [self.spellchecker.correct_spell(food) for food in foods]
        self.logger.log(logging.DEBUG, f"Step 2 correct spell:\nFOODS: {foods}")

        #Step 3: Mapping entities
        map_entities = mapping.map(foods, prices)

        self.logger.log(logging.INFO, f"Step 3 mapping:\n{map_entities}\n-----------------------------------------------------------")

        return map_entities
