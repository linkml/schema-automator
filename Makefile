.PHONY: all clean

all: clean target/soil_meanings.yaml

clean:
	rm -rf target/soil_meanings.yaml
	rm -rf target/soil_meanings_generated.yaml
	rm -rf target/availabilities_g_s_strain_202112151116.yaml
	rm -rf target/availabilities_g_s_strain_202112151116_org_meanings.yaml

# tried to find a single meaning for each permissible value
# unlike term mapping, which can tolerate multiple mapped terms
target/soil_meanings.yaml: tests/resources/mixs/terms.yaml
	poetry run enum_annotator \
		--modelfile $< \
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

# KeyError: 'iri' could mean that an unrecognized ontology name was used
target/availabilities_g_s_strain_202112151116_org_meanings.yaml: target/availabilities_g_s_strain_202112151116.yaml
	poetry run enum_annotator \
		--modelfile $< \
		--requested_enum_name organism_enum \
		--ontology_string NCBITAXON > $@

target/availabilities_g_s_strain_202112151116_org_meanings_curateable.tsv: target/availabilities_g_s_strain_202112151116_org_meanings.yaml
	poetry run enums_to_curateable \
		--modelfile $< \
		--enum organism_enum \
		--tsv_out $@

#target/availabilities_g_s_strain_202112151116_org_meanings_curated.yaml: target/availabilities_g_s_strain_202112151116_org_meanings_curated.tsv
#	poetry run curated_to_enums \
#		--tsv_in PATH         [required] \
#		--tsv_encoding TEXT   [default: utf_16] \
#		--model_in PATH       [required] \
#		--curated_yaml PATH   [default: curated.yaml] \
#		--selected_enum TEXT  [required]
