# NLP
# Named Entity Recognition, Part-Of-Speech Tagging, Text Cetegorization
# Coreference resolution, syntactic parsing, machine translation

# NLU
# Paraohrase & Natural inference, dialogues agents, semantic parsing,
# summarization, question answering, sentiment analysis.

# https://ngc.nvidia.com/catalog/collections/nvidia:jarvis

import torch
import nemo.collections.nlp as nemo_nlp
from nemo.utils.exp_manager import exp_manager

import os
import wget
import pytorch_lightning as pl
from omegaconf import OmegaConf

print(nemo_nlp.modules.get_pretrained_lm_models_list())
nemo_nlp.modules.get_lm_model(pretrained_model_name="distilbert-base-uncased")

# https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/nlp/models.html
# Intent Detection and slot tagging -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_intentdetectionandslottagging
#


# Named Entity Recognition -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_namedentityrecognition
# pretrained("ner_en_bert")
print(nemo_nlp.models.TokenClassificationModel.list_available_models())
model = nemo_nlp.models.TokenClassificationModel.from_pretrained("ner_en_bert")
results = model.add_predictions(['Mary lives in Santa Clara and works at NVIDIA.', 'we bought four shirts from the nvidia gear store in santa clara.', 'NVIDIA is a company.'])
print(results)


# Punctuation and capitalization -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_punctuationandcapitalization
# pretrained("punctuation_en_bert")


# Question Answering -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_questionanswering
# pretrained("qa_squadv1.1_bertbase)
print(nemo_nlp.models.QAModel.list_available_models())
model = nemo_nlp.models.QAModel.from_pretrained("qa_squadv1.1_bertbase")
#results = model.inference(['Hello', 'we bought four shirts from the nvidia gear store in santa clara.', 'NVIDIA is a company.'])
#print(results)


# Text classification -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_textclassification
#