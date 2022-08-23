import os
from typing import List

import mapping
from spellchecker import SpellChecker


class PostPreprocessor(object):
    def __init__(self):

        folder_path = os.path.dirname(__file__)

        self.spellchecker = SpellChecker(f'{folder_path}/food_vocabulary/one_gram.txt', f'{folder_path}/food_vocabulary/big_gram.txt')

    def preprocess(self, entities:List[str]):
        #Clean text
        text = "\n".join(entities)
        text = mapping.clean_raw_text(text)
        entities = text.split('\n')

        #Step 1: Classify food and prices
        foods, prices = mapping.get_price_and_food(entities)

        print(f"FOODS: {foods}")
        print(f"PRICES: {prices}")

        #Step 2: Correct spell for foo entities
        foods = [self.spellchecker.correct_spell(food) for food in foods]
        print(f" FOODS after correct spell {foods}")

        #Step 3: Mapping entities
        map_entities = mapping.map(foods, prices)

        return map_entities
