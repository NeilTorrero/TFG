#import stanfordcorenlp

#corenlp = stanfordcorenlp.StanfordCoreNLP(r'/home/neil/Downloads/stanford-corenlp-4.2.2/')
#print('Tokenize: ', corenlp.word_tokenize("Pipo is with all of us."))
#corenlp.close()


import stanza

#stanza.download('en')
#nlp = stanza.Pipeline('en', processors='tokenize, mwt, pos, lemma, depparse, ner, sentiment', use_gpu=True)
#doc = nlp("House has to get rid of one of the guys from his team.")
#print(doc)


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
stop_words = set(nltk.corpus.stopwords.words("english"))
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



import spacy

text = "House has to get rid of one of the guys from his team. And how are you."
spacy_model = spacy.load("en_core_web_trf")
result = spacy_model(text)
print(result)

# Sentence Segmentation
# Word Tokenization
# Key Phrase Extraction
# Part of Speech Tagging
# Named Entity Recognition
# Syntactic Parsing
# Entity Disambiguation
# Coreference Resolution
# Relation/Temporal/Event Extraction