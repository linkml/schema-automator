.PHONY: all clean

all: clean target/soil_meanings.yaml

clean:
	rm -rf target/soil_meanings.yaml
	rm -rf target/soil_meanings_generated.yaml
	rm -rf target/availabilities_g_s_strain_202112151116.yaml

# tried to find a single meaning for each permissible value
# unlike term mapping, which can tolerate multiple mapped terms
target/soil_meanings.yaml:
	poetry run enum_annotator \
		--modelfile tests/resources/mixs/terms.yaml \
		--requested_enum_name fao_class_enum \
		--ontology_string ENVO > $@

# validate that it's still valid LinkML
# FileNotFoundError: [Errno 2] No such file or directory: '/Users/MAM/Documents/gitrepos/linkml-model-enrichment/target/ranges.yaml'
# cp tests/resources/mixs/*yaml target
target/soil_meanings_generated.yaml: target/soil_meanings.yaml
	poetry run gen-yaml $< > $@

# requires Felix files
# add demonstration SQL file
target/availabilities_g_s_strain_202112151116.yaml: local/availabilities_g_s_strain_202112151116.tsv
	poetry run tsv2linkml \
		--enum-columns organism \
		--output $@ \
		--class_name availabilities \
		--schema_name availabilities $<
