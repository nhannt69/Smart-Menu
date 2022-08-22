import re

from symspellpy import SymSpell


class SpellChecker(object):
    def __init__(
        self, vocabulary_path: str, vocabulary_big_gram_path: str, edit_distance=3
    ):
        self.spell = SymSpell(edit_distance=edit_distance)
        self.ed = edit_distance

        self.spell.load_dictionary(vocabulary_path)

        if vocabulary_big_gram_path:
            self.spell.load_bigram_dictionary(vocabulary_big_gram_path)

    def correct_spell(self, text):
        """
        It takes a string, splits it into words, and then checks each word against the spellchecker. If the
        word is not in the dictionary, it will be replaced with the most likely suggestion

        :param text: The text to be corrected
        :return: The first suggestion from the spell checker.
        """
        text = text.lower()

        text = re.sub(r"[.\?#@+,<>%~`!$^&\(\):;\\\/]", r" \g<0> ", text)

        suggestion = self.spell.lookup_compound(
            text,
            max_edit_distance=self.ed,
            ignore_non_words=True,
            ignore_term_with_digits=True,
        )
        return suggestion[0]._term
