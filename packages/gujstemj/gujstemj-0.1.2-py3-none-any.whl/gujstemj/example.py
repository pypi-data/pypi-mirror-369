from gujstemj import stem_gujarati_word

word1 = "વાંચીએ"
stemmed_word1 = stem_gujarati_word(word1)
print(f"Original: {word1}, Stemmed: {stemmed_word1}")

word2 = "વિદ્યાર્થીઓ"
stemmed_word2 = stem_gujarati_word(word2)
print(f"Original: {word2}, Stemmed: {stemmed_word2}")

word3 = "કરવા"
stemmed_word3 = stem_gujarati_word(word3)
print(f"Original: {word3}, Stemmed: {stemmed_word3}")

word4 = "કંપની" # An indeclinable word
stemmed_word4 = stem_gujarati_word(word4)
print(f"Original: {word4}, Stemmed: {stemmed_word4}")