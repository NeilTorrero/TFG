import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.constants import (
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    ENTITY_ATTRIBUTE_VALUE,
    ENTITIES,
    EXTRACTOR,
)
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.model import Metadata
from transformers import pipeline

class EmotionExtractor(EntityExtractor):
    defaults = {}
    supported_language_list = ["en"]

    def required_components(cls) -> List[Type[Component]]:
        return []

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
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
        if msg is not None:
            prediction = self.model(msg)
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
            joy_score = 0
            sadness_score = 0
            for label in prediction[0]:
                if label['label'] == 'joy':
                    joy_score = label['score']
                if label['label'] == 'sadness':
                    sadness_score = label['score']
            
            labels = [{ENTITY_ATTRIBUTE_TYPE: 'joy',
                ENTITY_ATTRIBUTE_START: 0,
                ENTITY_ATTRIBUTE_END: 0,
                EXTRACTOR: 'emotion',
                ENTITY_ATTRIBUTE_VALUE: joy_score
            },{ENTITY_ATTRIBUTE_TYPE: 'sadness',
                ENTITY_ATTRIBUTE_START: 0,
                ENTITY_ATTRIBUTE_END: 0,
                EXTRACTOR: 'emotion',
                ENTITY_ATTRIBUTE_VALUE: sadness_score
            }]
            labels = self.add_extractor_name(labels)
            message.set(ENTITIES, message.get(ENTITIES, []) + labels, add_to_output=True)


    @classmethod
    def load(cls, meta: Dict[Text, Any], model_dir: Optional[Text] = None, model_metadat: Optional[Metadata] = None, cached_component: Optional["EmotionExtractor"] = None, **kwargs: Any) -> 'NeuralCoref':
        if cached_component:
            return cached_component

        return cls(meta)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass