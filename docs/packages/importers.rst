.. importers:

Importers
=========

Importers take either a representation of a schema in a different language or example data and bootstraps a schema.

Importers are the opposite of `Generalizers <https://linkml.io/linkml/generators/index.html>`_ in the core LinkML framework

.. warning::

   Generally importers take a *less expressive* language than LinkML and attempts to create the corresponding
   LinkML schema. This may be less optimal than a hand-crafted schema. For example, when converting to a
   representation that lacks `inheritance <https://linkml.io/linkml/schemas/inheritance.html>`_, no ``is_a`` slots
   will be created.

.. currentmodule:: schema_automator.importers

.. autoclass:: JsonSchemaImportEngine
    :members: create

.. autoclass:: OwlImportEngine
    :members: create

.. autoclass:: DOSDPImportEngine
    :members: create

