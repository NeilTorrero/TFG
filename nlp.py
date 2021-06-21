import torch
import nemo.collections.nlp as nemo_nlp
from nemo.utils.exp_manager import exp_manager

import os
import wget
import pytorch_lightning as pl
from omegaconf import OmegaConf

print(nemo_nlp.modules.get_pretrained_lm_models_list())
nemo_nlp.modules.get_lm_model(pretrained_model_name="distilbert-base-uncased")
