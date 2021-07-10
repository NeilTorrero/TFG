import spacy

text = "House has to get rid of one of the guys from his team. And how are you."
spacy_model = spacy.load("en_core_web_lg")

#spacy_model.enable_pipe("")
#aux_model = spacy.load("en_core_web_")
#spacy_model.add_pipe("component", source=aux_model)
print(spacy_model.pipe_names)


result = spacy_model(text)
print(result)

# Sentence Segmentation
# Word Tokenization
# Key Phrase Extraction
# POS Part of Speech Tagging
# NER Named Entity Recognition
# Syntactic Parsing
# Entity Disambiguation
# Coreference Resolution
# Relation/Temporal/Event Extraction
