import re

from symspellpy import SymSpell, Verbosity


class SpellChecker(object):
    def __init__(
        self, vocabulary_path: str, vocabulary_big_gram_path: str=None, edit_distance=3, prefix_length=10
    ):
        self.spell = SymSpell(
            max_dictionary_edit_distance=edit_distance, prefix_length=prefix_length
        )
        self.ed = edit_distance

        self.spell.load_dictionary(
            vocabulary_path, 0, 1, separator="$", encoding="utf-8"
        )

        if vocabulary_big_gram_path:
            self.spell.load_bigram_dictionary(
                vocabulary_big_gram_path, 0, 1, separator="$", encoding="utf-8"
            )

    def correct_spell(self, text, lookup_only=True, include_unknown=False):
        """
        It takes a string, splits it into words, and then checks each word against the spellchecker. If the
        word is not in the dictionary, it will be replaced with the most likely suggestion
        :param text: The text to be corrected
        :return: The first suggestion from the spell checker.
        """

        if not text:
            return text

        text = text.lower()

        if lookup_only:
            suggestion = self.spell.lookup(
                text, Verbosity.CLOSEST, include_unknown=include_unknown
            )
        else:
            suggestion = self.spell.lookup_compound(
                text,
                max_edit_distance=self.ed,
                ignore_non_words=True,
                ignore_term_with_digits=True,
            )

        if not suggestion:
            return ""

        return suggestion[0]._term
