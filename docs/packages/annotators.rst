Annotators
==========

Importers take an existing schema and *annotate* it with information

Annotators typically talk to an external ontology. We use the OAK library to wrap a large number
of different sources that can be used for annotation, including:

- BioPortal
- OLS/ZOOMA
- Arbitrary ontologies in obo format, OWL, RDF, or JSON
- Ubergraph
- Wikidata
- LOV

For documentation on selecting the right ontology source, see:

- `Selectors <https://incatools.github.io/ontology-access-kit/selectors.html>`_

.. currentmodule:: schema_automator.annotators

.. autoclass:: SchemaAnnotator
    :members:

.. autoclass:: JsonLdAnnotator
    :members:

.. autoclass:: LLMAnnotator
    :members:
