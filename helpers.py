from __future__ import print_function
import os
import requests
import urllib.parse
import time
from flask import redirect, render_template, request, session
from functools import wraps
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
import pprint
from textblob import TextBlob
from spellchecker import SpellChecker
import wikipedia

import re


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_entities_dict(p_str):
    """
    Uses SpaCy en_core_web_sm to find entities from the text the user writes

    Returns a dictionary containing entities grouped by their type
    """
    nlp = en_core_web_sm.load()
    doc = nlp(p_str)
    entities = {}
    relevant_keywords = []
    list_of_types = ['NORP', 'ORG', 'GPE', 'LAW', 'LANGUAGE']
    for X in doc.ents:
        if not(X.label_ in entities):
            entities[X.label_] = []
        entities[X.label_].append(X.text)
        if X.label_ in list_of_types:
            relevant_keywords.append(X.text)
    print(entities)
    print("HERE")
    print(relevant_keywords)
    return entities, relevant_keywords


def get_sentiment(p_str):
    """
    Uses TextBlob to find two stats related to a string's sentiments

    Returns a dictionary of the two stats
    """
    processed = TextBlob(p_str)
    return({'polarity': round(processed.sentiment.polarity,3), 'subjectivity': round(processed.sentiment.subjectivity, 3)})


def spelling(p_str):
    """
    Uses PySpellChecker to run spell check

    Detects misspelled words and provides possible suggestions
    """
    spell = SpellChecker(language='en')
    misspelled = spell.unknown(re.sub(r'[^\w\s]', '', p_str).split())
    corrections = {}
    for word in misspelled:
        tmp = list(spell.candidates(word))
        tmp.insert(0, spell.correction(word))
        corrections[word] = tmp
    return(corrections)


def get_related_words(p_word):
    keyword = p_word
    related = wikipedia.search(keyword)
    if related  == []:
        keyword = wikipedia.suggest(keyword)
    return(wikipedia.search(keyword)[:10] + wikipedia.page(keyword).links[:10])
