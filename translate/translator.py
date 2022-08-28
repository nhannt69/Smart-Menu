import json


class DictionaryTranslator(object):
    def __init__(self, dictionary_path):
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)

    def translate(self, text):
        text = text.lower()
        return self.dictionary.get(text, text)
