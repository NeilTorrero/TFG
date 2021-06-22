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
# Punctuation and capitalization -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_punctuationandcapitalization
# pretrained("punctuation_en_bert")
# Question Answering -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_questionanswering
# pretrained("qa_squadv1.1_bertbase)
# Text classification -> https://ngc.nvidia.com/catalog/collections/nvidia:tlt_jarvis_textclassification
#