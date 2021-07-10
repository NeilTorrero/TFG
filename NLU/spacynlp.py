import spacy

text = "House has to get rid of one of the guys from his team. And how are you."
spacy_model = spacy.load("en_core_web_lg")

#spacy_model.enable_pipe("")
#aux_model = spacy.load("en_core_web_")
#spacy_model.add_pipe("component", source=aux_model)
print(spacy_model.pipe_names)


result = spacy_model(text)
# Sentence Segmentation
print(result.text)

# Word Tokenization
for token in result:
    print(token.text)
# Key Phrase Extraction
# POS Part of Speech Tagging
    print(token.tag_)
# NER Named Entity Recognition
    print(token.ent_iob_, token.ent_type_)
# Syntactic Parsing
    print(token.dep_)
# Entity Disambiguation
# Coreference Resolution
# Relation/Temporal/Event Extraction
