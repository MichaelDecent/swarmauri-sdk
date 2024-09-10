import json
from typing import List, Literal, Dict
from transformers import pipeline, logging as hf_logging
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter
from pydantic import Field

hf_logging.set_verbosity_error()

class EntityRecognitionTool(ToolBase):
    """
    A tool that extracts named entities from text using a pre-trained NLP model.
    """
    name: str = "EntityRecognitionTool"
    description: str = "Extracts named entities from text"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text for entity recognition",
                required=True
            )
        ]
    )
    type: Literal['EntityRecognitionTool'] = 'EntityRecognitionTool'

    def __call__(self, text: str) -> Dict[str, str]:
        try:
            self.nlp = pipeline("ner")
            entities = self.nlp(text)
            organized_entities = {}
            for entity in entities:
                if entity['entity'] not in organized_entities:
                    organized_entities[entity['entity']] = []
                organized_entities[entity['entity']].append(entity['word'])
            return json.dumps(organized_entities)
        except Exception as e:
            raise e
        finally:
            del self.nlp
