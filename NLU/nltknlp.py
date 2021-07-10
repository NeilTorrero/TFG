import nltk

# nltk.download()

# Sentence Segmentation
text = "House has to get rid of one of the guys from his team. And how are you."
sentenceseg = nltk.tokenize.punkt.PunktSentenceTokenizer()
segmented = sentenceseg.tokenize(text)
print("Segmented sentence: ")
print(segmented)

# Word Tokenization
tokenizer = nltk.tokenize.WhitespaceTokenizer()
tokenized = tokenizer.tokenize(segmented[0])
print("Tokenized: ")
print(tokenized)

# Remove Stop Words
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))
tokenized_nosw = []
for word in tokenized:
    if word.casefold() not in stop_words:
        tokenized_nosw.append(word)
print("Filtered Stop Words")
print(tokenized_nosw)

# Key Phrase Extraction
import textacy

# Part of Speech Tagging
pos_text = nltk.pos_tag(tokenized)
print("POS: ")
print(pos_text)

# Named Entity Recognition
print("NER: ")
print(nltk.ne_chunk(pos_text))

# Syntactic Parsing
# do with nlpcore

# Entity Disambiguation

# Coreference Resolution
# Relation/Temporal/Event Extraction
