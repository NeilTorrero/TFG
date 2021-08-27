import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata
from transformers import pipeline


class EmotionExtractor(Component):
    name = "EmotionExtractor"
    defaults = {}
    supported_language_list = ["en"]

    def required_components(cls) -> List[Type[Component]]:
        return []

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        from transformers import pipeline
        self.model = pipeline("text-classification",model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)
        

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def process(self, message: Message, **kwargs: Any) -> None:
        msg = message.get(TEXT)
        prediction = self.model(msg, )
        print(prediction)
        """
        Output:
        [[
        {'label': 'sadness', 'score': 0.0006792712374590337}, 
        {'label': 'joy', 'score': 0.9959300756454468}, 
        {'label': 'love', 'score': 0.0009452480007894337}, 
        {'label': 'anger', 'score': 0.0018055217806249857}, 
        {'label': 'fear', 'score': 0.00041110432357527316}, 
        {'label': 'surprise', 'score': 0.0002288572577526793}
        ]]
        """
        labels = {"entity": "emotion",
            "extractor": "emotion_extractor",
            "labels": prediction[0]
        } 
        # try with rasa.shared.core.tracker
        # api call to set the slots
        # action called to make the avg
        # make list entity

        message.set("entities", [labels], add_to_output=True)


    @classmethod
    def load(cls, meta: Dict[Text, Any], model_dir: Optional[Text] = None, model_metadat: Optional[Metadata] = None, cached_component: Optional['NeuralCoref'] = None, **kwargs: Any) -> 'NeuralCoref':
        if cached_component:
            return cached_component

        return cls(meta)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass