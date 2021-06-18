from omegaconf import OmegaConf, open_dict
import torch
from nemo.collections.asr.parts import parsers
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder


def load_spectrogram_model():
    override_conf = None
    from nemo.collections.tts.models import Tacotron2Model
    pretrained_model = "tts_en_tacotron2"

    model = SpectrogramGenerator.from_pretrained(pretrained_model, override_config_path=override_conf)
    return model


def load_vocoder_model():
    from nemo.collections.tts.models import WaveGlowModel
    pretrained_model = "tts_waveglow_88m"
    model = Vocoder.from_pretrained(pretrained_model)
    return model


spec_gen = load_spectrogram_model().cuda()
vocoder = load_vocoder_model().cuda()


def infer(spec_gen_model, vocder_model, str_input):
    with torch.no_grad():
        parsed = spec_gen.parse(str_input)
        spectrogram = spec_gen.generate_spectrogram(tokens=parsed)
        audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)
    if isinstance(spectrogram, torch.Tensor):
        spectrogram = spectrogram.to('cpu').numpy()
    if len(spectrogram.shape) == 3:
        spectrogram = spectrogram[0]
    if isinstance(audio, torch.Tensor):
        audio = audio[0].to('cpu').numpy()
    return spectrogram, audio

text_to_generate = input("Input what you want the model to say: ")
spec, audio = infer(spec_gen, vocoder, text_to_generate)

import IPython.display as ipd
import numpy as np
from PIL import Image
from scipy.io.wavfile import write
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

import playsound

ipd.Audio(audio, rate=22050)
write("audio.wav", 22050, audio)

imshow(spec, origin="lower")
plt.show()