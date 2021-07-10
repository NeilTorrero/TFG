import stanfordcorenlp

corenlp = stanfordcorenlp.StanfordCoreNLP(r'/home/neil/Downloads/stanford-corenlp-4.2.2/')
print('Tokenize: ', corenlp.word_tokenize("Pipo is with all of us."))
corenlp.close()


import stanza

stanza.download('en')
nlp = stanza.Pipeline('en', processors='tokenize, mwt, pos, lemma, depparse, ner, sentiment', use_gpu=True)
doc = nlp("House has to get rid of one of the guys from his team.")
print(doc)