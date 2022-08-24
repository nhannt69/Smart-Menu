from googletrans import Translator
import pandas as pd

df = pd.read_excel("data_sample\Data_Labeling.xlsx")

df_filter = df.loc[0, 'VietnameseName']

trans = Translator()
count = 0
for index in range(df.shape[0]):
    string = df.loc[index, "VietnameseName"]
    string_trans = trans.translate(string, dest='en', src='vi').text.upper()
    if string_trans == df.loc[index, "EnglishName"]:
        count += 1
    print(count)
print (count)