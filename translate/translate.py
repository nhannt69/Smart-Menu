"""
Final step: alter mapping succesfully, your output this above step is menu which is list contains inside many tuple
Input: list loop
Output: list loop but each item is a tuple has three element: ('food_name', 'price', 'food_en')

"""
from googletrans import Translator


class Translator_Menu(object):
    def __init__(self):
        self.translator = Translator()

    def process_translate(self, menu):

        pairs = []

        for item in menu:
            translation = self.translator.translate(item[0], dest='en', src='vi')
            translated_name = translation.text
            item += [translated_name.upper()]
            pairs.append((item[0].upper(), item[1], item[2]))
        return pairs

if __name__ =='__main__':
    menu = [['Rau muống xào tỏi', '20000'],['Bắp cải xào tỏi', '150000'],['Đậu xào', '145800'],['Gà nướng', '45000']]
    translator = Translator_Menu()
    print(translator.process_translatate(menu=menu))

