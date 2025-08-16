# -*- coding: utf-8 -*-
# gujarati_stemmer/stemmer.py

# List of common Gujarati suffixes.
# These will be sorted by length (longest first) to ensure correct removal.
# The suffixes are provided by the user.
GUJARATI_SUFFIXES = [
    'એ', 'ે', 'ઓ', 'ો', 'ને', 'ઓને', 'ોને', 'ે', 'એ', 'થી', 'થકી', 'વડે', 'દ્વારા', 'ોએ', 'ઓએ', 'ઓથી', 'ઓથકી',
    'ઓવડે', 'ઓદ્વારા', 'અર્થે', 'કાજે', 'ને માટે', 'ને વાસ્તે', 'ને સારુ', 'ોઅર્થે', 'ોકાજે', 'ોને માટે',
    'ોને વાસ્તે', 'ોને સારુ', 'થી', 'ઉપરથી', 'માંથી', 'અંદરથી', 'પરથી', 'ોથી', 'ોથકી', 'ઓથી', 'ઓ થકી',
    'નો', 'ની', 'નું', 'ના', 'ોનો', 'ોની', 'ોનું', 'ોના', 'માં', 'માંહે', 'અંદર', 'ઉપર', 'પર', 'નીઅંદર',
    'ોમાં', 'ો માંહે', 'ો ઉપર', 'ો પર', 'ો નીઅંદર', 'ઉ છું', 'ુ છું', 'ઇએ છીએ', 'ીએ છીએ','ીએ', 'એ છે','ે છે',
    'ઓ છો', 'ો છો', 'એ છે', 'ે છે', 'એ છે', 'ે છે', 'યો', 'ો', 'યા', 'ા', 'યો', 'યા', 'ા', 'યો', 'ો', 'યા',
    'ા', 'યા', 'ા', 'ી', 'યા', 'ા', 'ી', 'યા', 'ા', 'યુ', 'ુ', 'યા', 'ા', 'યુ', 'ુ', 'યા', 'ા', 'યુ', 'ુ',
    'યા', 'ીશ', 'શુ', 'શે', 'શો','ીશુ','ોને'
]

# Sort suffixes by length in descending order to prevent partial matches
GUJARATI_SUFFIXES.sort(key=len, reverse=True)

# List of indeclinable words (provided by the user).
# These words are their own roots.
INDECLINABLE_WORDS = {
    'નો', 'ક્યારે', 'તક', 'કેવું', 'કેવુ', 'કેવા', 'કેવાં', 'કેવી', 'ક્યાં', 'ક્યા', 'ક્યારે', 'હું', 'હુ',
    'મેં', 'મે', 'પોતે', 'તું', 'તુ', 'તમે', 'તમારો', 'તમારા', 'તમારું', 'તમારુ', 'તમારાં', 'તારી', 'તમારી',
    'અમે', 'અમારે', 'અમારી', 'અમારું', 'અમારુ', 'તે', 'તેઓ', 'તમારા', 'તમારાં', 'તમને', 'સુઘી', 'સ્ત્રી',
    'પરથી', 'ની', 'થી', 'એ', 'માં', 'તો', 'રોજ', 'જયારે', 'પણ', 'અંદર', 'નીચે', 'ઉપરાંત', 'આજુબાજુ', 'વાસ્તે',
    'વડે', 'ઉપર', 'કે', 'અથવા', 'પછી', 'દૂર', 'માંહે', 'જેથી', 'પર', 'માટે', 'સારુ', 'અર્થે', 'જેમ', 'તથા',
    'જ્યાં', 'તેથી', 'અને', 'માંથી', 'બારેબાર', 'જ્યા', 'સમાન', 'પ્રત્યે', 'હમણાં', 'હમણા', 'ત્યાં', 'સારું',
    'કાલે', 'તરફ', 'બહાર', 'નહીં', 'છીએ', 'ત્યા', 'માહે', 'જેમાં', 'ત્યારે', 'દ્વારા', 'ના', 'જલદી', 'અહી',
    'પાસે', 'ઉપરથી', 'હવે', 'કાજે', 'અહીં', 'ખાતર', 'સાંજે', 'સુધી', 'બરાબર', 'હેતુ', 'અહીંયા', 'સાચુ',
    'તરત', 'થકી', 'પાછળ', 'હેતું', 'સાચું', 'પ્રતિ', 'ક્યાં', 'ક્યા', 'નહી', 'બાદ', 'જલ્દી', 'ફાયદો', 'પૂજા',
    'રેખા', 'થશે', 'થતું', 'થતુ', 'કેરી', 'કંપની'
}

def stem_gujarati_word(word: str) -> str:
    """
    Stems a single Gujarati word to find its root form.

    Args:
        word (str): The Gujarati word to stem.

    Returns:
        str: The stemmed root word.
    """
    # 1. For Gujarati, ensure consistent character representation if there are variations.
    processed_word = word.strip()

    # 2. Check if the word is in the list of indeclinables.
    #    If it is, return the word itself as its root.
    if processed_word in INDECLINABLE_WORDS:
        return processed_word

    # 3. Apply suffix removal rules.
    #    Iterate through sorted suffixes (longest first).
    for suffix in GUJARATI_SUFFIXES:
        if processed_word.endswith(suffix):
            # Remove the suffix and return the remaining part.
            # changes the last character of the stem in a specific way.
           return processed_word[:-len(suffix)]

    # If no suffix is matched and it's not an indeclinable,
    # the word itself is considered the root.
    return processed_word