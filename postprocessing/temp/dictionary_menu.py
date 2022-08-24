from time import time
import numpy as np
import pandas as pd
import difflib

class Formating_Dictionary(object):
    def __init__(self, file_path_dict):
        self.file_path_dict = file_path_dict

    def compute_different_word(self, str_name_food, str_name_sample):
        """
        function used to compute the similar between two word 
        in list item name food into dictionary
        """
        percentage = 0
        try:
            seq = difflib.SequenceMatcher(None, str_name_food, str_name_sample)
            percentage = seq.ratio()*100
        except:
            percentage = 0
            pass
        return percentage

    def remove_accent(self, input_str):
        """
            https://gist.github.com/J2TEAM/9992744f15187ba51d46aecab21fd469
            with SequenceMatcher, it auto remove accent
        """
        s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
        s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
        s = ''
        for c in input_str:
            if c in s1:
                s += s0[s1.index(c)]
            else:
                s += c
        return s

    def format_result_dict(self, name_food):
        """
        function use to find item Vietnamese name food 
        it return name have best similar with name food input
        threadhold is 50
        """
        # try:
        import time
        start = time.time()
        result_str, max_percentage = None, 0
        dataframe = pd.read_excel(self.file_path_dict)
        list_item_name = dataframe.loc[:, 'Name'].values
        list_diff_word = [int(self.compute_different_word(name_food.upper(), item)) for item in list_item_name]
        max_percentage = np.max(list_diff_word)         
        index = list_diff_word.index(max_percentage)
        # print(max_percentage)
        # except (RuntimeError, TypeError, NameError) as info:
        #     print(info)
        
        if  max_percentage > 50:
            result_str = dataframe.loc[index, 'EnglishName']
        else:
            result_str = name_food
        
        return result_str, time.time() - start

    

if __name__ == '__main__':

    Result = Formating_Dictionary('postprocessing\dictionary_menu.xlsx')

    import time

    start = time.time()

    name_food_test = 'TIGER BẠC LON'

    print(f"Result word is best similar is {Result.format_result_dict(name_food_test)}")

    print(time.time() - start)
