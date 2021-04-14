export PYTHONPATH=.
# .PHONY:  inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml

# https://docs.google.com/spreadsheets/d/1VFeUZqLmnmXDS1JcyXQbMgF513WyUBgz/edit#gid=1742629071

tests: unit-tests integration-tests

unit-tests:
	pytest tests/unit/*.py

integration-tests:
	pytest tests/*.py

typecheck:
	mypy kgx --ignore-missing-imports

# samples of mapping enumerables to semantic terms via BioPortal 
species_enum_ncbitaxon: inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml
	linkml_model_enrichment/bioportal-enum-annotation.py \
	--modelfile inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml \
	--enum_source species_enum \
	--ontoprefix ncbitaxon > target/species_enum_ncbitaxon.yaml
	
species_enum_all_bp: inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml
	linkml_model_enrichment/bioportal-enum-annotation.py --modelfile inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml --enum_source species_enum > target/species_enum_all_bp.yaml

type_enum_so: inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml
	linkml_model_enrichment/bioportal-enum-annotation.py --modelfile inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml --enum_source type_enum --ontoprefix so > target/type_enum_so.yaml

inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml:
	linkml_model_enrichment/infer_model.py \
	tsv2model \
	-E species \
	data/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.tsv > \
	inferred-models/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml