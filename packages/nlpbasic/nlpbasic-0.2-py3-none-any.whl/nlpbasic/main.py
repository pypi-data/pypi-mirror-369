"""
mynlp - A lightweight, pure-Python NLP preprocessing library
Author: ADITI PAWAR
"""

import re

# Default stopword list
STOPWORDS = {
    "a", "an", "the", "and", "or", "is", "are", "was", "were", "in", "on",
    "for", "with", "of", "to", "by", "from", "at", "it", "this", "that",
    "as", "be", "has", "have", "had", "do", "does", "did", "but", "if"
}

class NLPProcessor:
    """
    Pure-Python NLP Processor for:
    - Basic text cleaning
    - Stopword removal
    - Simple lemmatization
    - Simple stemming
    """

    def __init__(self, stopwords=None):
        """
        Initialize processor with optional custom stopword set.
        """
        self.stopwords = set(stopwords) if stopwords else STOPWORDS

    def basic_clean(self, text):
        """
        Lowercase and remove punctuation/numbers.
        """
        text = text.lower()
        return re.sub(r"[^a-z\s]", "", text).strip()

    def remove_stopwords(self, tokens):
        """
        Remove common stopwords.
        """
        return [word for word in tokens if word not in self.stopwords]

    def basic_stem(self, word):
        """
        Very simple stemming (rule-based).
        """
        suffixes = ["ing", "ed", "es", "s", "ly"]
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        return word

    def basic_lemmatize(self, word):
        """
        Very simple lemmatization (rule-based).
        """
        lemmas = {
            "cats": "cat",
            "mice": "mouse",
            "geese": "goose",
            "children": "child",
            "men": "man",
            "women": "woman",
            "running": "run",
            "ran": "run",
            "better": "good",
            "best": "good"
        }
        return lemmas.get(word, word)

    def process(self, text):
        """
        Full NLP pipeline: cleaning → tokenizing → stopword removal → lemmatization → stemming.
        """
        text = self.basic_clean(text)
        tokens = text.split()
        tokens = self.remove_stopwords(tokens)
        tokens = [self.basic_lemmatize(word) for word in tokens]
        tokens = [self.basic_stem(word) for word in tokens]
        return tokens