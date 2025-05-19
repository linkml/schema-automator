.. _cli:

Command Line Interface
======================

All Schema Automator functionality is available via the ``schemauto`` command.

Preamble
--------

.. warning::

   Previous versions had specific commands like ``tsv2linkml`` these are now deprecated.
   Instead these are now *subcommands* of the main ``schemauto`` command, and have been renamed.

.. note::

   we follow the `CLIG <https://clig.dev/>`_ guidelines as far as possible

Main commands
-------------

.. currentmodule:: schema_automator.cli

.. click:: schema_automator.cli:main
    :prog: schemauto
    :show-nested:
