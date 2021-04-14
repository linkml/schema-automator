export PYTHONPATH=.
.PHONY:  species_enum_ncbitaxon species_enum_all_bp type_enum_so

tests: unit-tests integration-tests

unit-tests:
	pytest tests/unit/*.py

integration-tests:
	pytest tests/*.py

typecheck:
	mypy kgx --ignore-missing-imports

# samples of mapping enumerables to semantic terms via BioPortal 
 species_enum_ncbitaxon:
	linkml_model_enrichment/bioportal-enum-annotation.py --modelfile inferred-models/synbio.yaml --enum_source species_enum --ontoprefix ncbitaxon > target/species_enum_ncbitaxon.yaml
	
 species_enum_all_bp:
	linkml_model_enrichment/bioportal-enum-annotation.py --modelfile inferred-models/synbio.yaml --enum_source species_enum > target/species_enum_all_bp.yaml

 type_enum_so:
	linkml_model_enrichment/bioportal-enum-annotation.py --modelfile inferred-models/synbio.yaml --enum_source type_enum --ontoprefix so > target/type_enum_so.yaml

