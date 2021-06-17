import nemo
import nemo.collections.asr as nemo_asr
import nemo.collections.nlp as nemo_nlp
import nemo.collections.tts as nemo_tts

from omegaconf import OmegaConf
import copy

if __name__ == '__main__':
    print(nemo.__version__)
    quartznet = nemo_asr.models.EncDecCTCModel.from_pretrained('QuartzNet15x5Base-En')
    quartznet.summarize()

    cfg = copy.deepcopy(quartznet.cfg)
    print(OmegaConf.to_yaml(cfg))
