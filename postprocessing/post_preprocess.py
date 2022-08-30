import logging
import os
from datetime import date
from typing import List

import mapping
from spellchecker import SpellChecker


class PostPreprocessor(object):
    def __init__(self, debug=False):

        folder_path = os.path.dirname(__file__)

        self.spellchecker = SpellChecker(
            f"{folder_path}/food_vocabulary/one_gram.txt",
            f"{folder_path}/food_vocabulary/big_gram.txt"
        )

        self.logger = self.__init__logger(debug)

    def __init__logger(self, debug):
        logger = logging.getLogger(__name__)
        fh = logging.FileHandler(
            f"{os.path.dirname(__file__)}/test_log/post_results_{date.today()}.log",
            mode="w",
            encoding="utf-8",
        )
        f_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s\n"
        )
        fh.setFormatter(f_format)

        log_level = logging.DEBUG if debug else logging.INFO

        #fh.setLevel(logging.DEBUG)
        logger.setLevel(log_level)

        logger.addHandler(fh)

        return logger

    def preprocess(self, entities: List[str]):
        self.logger.debug(f"Input entities: {entities}")
        # Clean text
        raw_text = "\n".join(entities)
        text = mapping.clean_raw_text(raw_text)
        entities = text.split("\n")
        self.logger.debug(f"After clean entities: {entities}")

        # Step 1: Classify food and prices
        foods, prices = mapping.get_price_and_food(entities)
        self.logger.log(
            logging.DEBUG, f"Step 1 classify: \nFOODS: {foods}\nPRICES: {prices}"
        )

        # Step 2: Correct spell for foo entities
        foods = [self.spellchecker.correct_spell(food, lookup_only=False, include_unknown=True) for food in foods]
        self.logger.log(logging.DEBUG, f"Step 2 correct spell:\nFOODS: {foods}")

        #Get size entities
        sizes = mapping.get_size(raw_text)

        # Step 3: Mapping entities
        map_entities = mapping.map(foods, prices, sizes)

        left_over_foods = [f for f in foods if f]
        for f in left_over_foods:
            map_entities.append([f, "NOT GIVEN"])

        #Spell check again
        #map_entities = [[self.spellchecker.correct_spell(f), p] for f, p in map_entities]

        #Clean empty entities
        map_entities = [[f, p] for f, p in map_entities if f]


        self.logger.log(
            logging.DEBUG,
            f"Step 3 mapping:\n{map_entities}",
        )

        return map_entities
