import logging
from dataclasses import dataclass
from typing import Union, Optional

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition

from schema_automator.annotators import SchemaAnnotator

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a LinkML schema assistant and your job is to suggest
values for missing elements in the schema.
Schema details: {schema_info}
"""

def enrich_using_llm(schema: Union[SchemaDefinition, str], model_name: str = None) -> SchemaDefinition:
    """
    Use the LLM model to enrich the schema with descriptions for elements that are missing them.

    Requires installation with the llm extra.

    :param schema:
    :param model_name:
    :return:
    """
    from llm import get_model, Conversation
    if not model_name:
        model_name = "gpt-4-turbo"
    model = get_model(model_name)
    sv = SchemaView(schema)
    schema = sv.schema
    schema_info =f"name: {schema.name}, description: {schema.description}"
    system_prompt = SYSTEM_PROMPT.format(schema_info=schema_info)
    logger.info(f"System: {system_prompt}")
    for elt in sv.all_elements().values():
        typ = elt.__class__.__name__
        if not elt.description:
            prompt = (f"Generate a description for the {typ} with name '{elt.name}'"
                      "The description should be a concise phrase that describes the element.")
            conversation = Conversation(model=model)
            result = conversation.prompt(prompt, system_prompt)
            elt.description = result.text()
            logger.debug(f"Updated Description: {elt.description}")
    return schema


@dataclass
class LLMAnnotator(SchemaAnnotator):
    """
    Annotates a schema using an LLM.
    """

    model_name: Optional[str] = None

    def enrich(self, schema: Union[SchemaDefinition, str]) -> SchemaDefinition:
        """
        Enrich a schema using an LLM.

        >>> from schema_automator.utils.schemautils import write_schema
        >>> annotator = LLMAnnotator(model_name="gpt-4")
        >>> schema = annotator.enrich("tests/resources/biopax3.yaml")
        >>> write_schema(schema)

        Requires installation with the llm extra:

        .. code-block:: bash

            pip install schema-automator[llm]

        Note: exercise caution on running this on large schemas with expensive
        models like gpt-4.

        :param schema:
        :return:
        """
        return enrich_using_llm(schema, model_name=self.model_name)
