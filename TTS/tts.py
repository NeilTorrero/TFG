supported_spec_gen = ["tacotron2", "glow_tts"]
supported_audio_gen = ["waveglow", "squeezewave", "uniglow", "melgan", "hifigan", "two_stages"]

print("Choose one of the following spectrogram generators:")
print([model for model in supported_spec_gen])
spectrogram_generator = input()
print("Choose one of the following audio generators:")
print([model for model in supported_audio_gen])
audio_generator = input()

assert spectrogram_generator in supported_spec_gen
assert audio_generator in supported_audio_gen

if audio_generator=="two_stages":
    print("Choose one of the following mel-to-spec convertor:")
    supported_mel2spec = ["psuedo_inverse"]
    print([model for model in supported_mel2spec])
    mel2spec = input()
    print("Choose one of the following linear spectrogram vocoders:")
    supported_linear_vocoders = ["griffin_lim"]
    print([model for model in supported_linear_vocoders])
    linvocoder = input()
    assert mel2spec in supported_mel2spec
    assert linvocoder in supported_linear_vocoders

from omegaconf import OmegaConf, open_dict
import torch
from nemo.collections.asr.parts import parsers
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder


def load_spectrogram_model():
    override_conf = None
    if spectrogram_generator == "tacotron2":
        from nemo.collections.tts.models import Tacotron2Model
        pretrained_model = "tts_en_tacotron2"
    elif spectrogram_generator == "glow_tts":
        from nemo.collections.tts.models import GlowTTSModel
        pretrained_model = "tts_en_glowtts"
        import wget
        from pathlib import Path
        if not Path("cmudict-0.7b").exists():
            filename = wget.download("http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b")
            filename = str(Path(filename).resolve())
        else:
            filename = str(Path("cmudict-0.7b").resolve())
        conf = SpectrogramGenerator.from_pretrained(pretrained_model, return_config=True)
        if "params" in conf.parser:
            conf.parser.params.cmu_dict_path = filename
        else:
            conf.parser.cmu_dict_path = filename
        override_conf = conf
    else:
        raise NotImplementedError

    model = SpectrogramGenerator.from_pretrained(pretrained_model, override_config_path=override_conf)
    return model


def load_vocoder_model():
    RequestPseudoInverse = False
    TwoStagesModel = False

    if audio_generator == "waveglow":
        from nemo.collections.tts.models import WaveGlowModel
        pretrained_model = "tts_waveglow_88m"
    elif audio_generator == "squeezewave":
        from nemo.collections.tts.models import SqueezeWaveModel
        pretrained_model = "tts_squeezewave"
    elif audio_generator == "uniglow":
        from nemo.collections.tts.models import UniGlowModel
        pretrained_model = "tts_uniglow"
    elif audio_generator == "melgan":
        from nemo.collections.tts.models import MelGanModel
        pretrained_model = "tts_melgan"
    elif audio_generator == "hifigan":
        from nemo.collections.tts.models import HifiGanModel
        pretrained_model = "tts_hifigan"
    elif audio_generator == "two_stages":
        from nemo.collections.tts.models import TwoStagesModel
        cfg = {'linvocoder': {'_target_': 'nemo.collections.tts.models.two_stages.GriffinLimModel',
                              'cfg': {'n_iters': 64, 'n_fft': 1024, 'l_hop': 256}},
               'mel2spec': {'_target_': 'nemo.collections.tts.models.two_stages.MelPsuedoInverseModel',
                            'cfg': {'sampling_rate': 22050, 'n_fft': 1024,
                                    'mel_fmin': 0, 'mel_fmax': 8000, 'mel_freq': 80}}}
        model = TwoStagesModel(cfg)
        if mel2spec == "encoder_decoder":
            from nemo.collections.tts.models.ed_mel2spec import EDMel2SpecModel
            pretrained_mel2spec_model = "EncoderDecoderMelToSpec-22050Hz"
            mel2spec_model = EDMel2SpecModel.from_pretrained(pretrained_mel2spec_model)
            model.set_mel_to_spec_model(mel2spec_model)

        if linvocoder == "degli":
            from nemo.collections.tts.models.degli import DegliModel
            pretrained_linvocoder_model = "DeepGriffinLim-22050Hz"
            linvocoder_model = DegliModel.from_pretrained(pretrained_linvocoder_model)
            model.set_linear_vocoder(linvocoder_model)

        TwoStagesModel = True

    else:
        raise NotImplementedError

    if not TwoStagesModel:
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