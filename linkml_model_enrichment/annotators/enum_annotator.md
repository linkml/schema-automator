# `webmap_enums.py` documentation



`webmap_enums.py` reads the labels of enums in a LinkML model and submits them to a web-based term mapping service. Rudimentary code for using the BioPortal annotator has been commented out as the OLS term search has be emphasized in recent development effort.

 All of the mappings are written to a TSV (`mappings_log.tsv` by default) file specified by `--tabular_outputfile`

The enums' descriptions and meanings can be overwritten if the following two conditions are true:

- If the cosine distance between the enum's label and the best search result's label or synonyms is less than or equal to the threshold (`--maxdist`, 0.05)
- If there was no meaning in the input, or if the `--overwite_meaning` is set

The model is written out to `STDOUT`, whether any enums have been updated or not.

`webmap_enums.py` should be executed from the `linkml-model-enrichment` repo's root directory. The input files mentioned in the examples below are not guaranteed to be present in a cloned `linkml-model-enrichment` repo.

**Convert a TSV file into a LinkML YAML file**
linkml_model_enrichment/infer_model.py tsv2model -E Taxon -E FAO -E Engineering tests/resources/webmap_enums.tsv > target/webmap_enums.yaml

**Map taxon-related enums from a sample file to NCBItaxon terms, without overwriting anything**

```bash
./linkml_model_enrichment/enum_annotator.py \
--verbosity DEBUG \
--modelfile target/webmap_enums.yaml \
--tabular_outputfile target/ncbitaxon_mappings_log.tsv \
--ontoprefix ncbitaxon \
--enum_list Taxon_enum \
--search_engine OLS > target/ncbitaxon_mappings.yaml
```

*That takes a little less than 2 minutes for 26 enum lables, on a 2020 Intel MacBook Pro with a 200 Mbps network connection. `webmap_enums.py` has not been optimized for speed in any way. The greatest time cost appears to come from waiting for responses from the search engine. While the BioPortal annotator indicates which portion of the enum label was matched to which property of the matched terms as part of the search itself, retrieving the same information from OLS requires retrieving the term details for each matched term. One example of a potential improvement to `webmap_enums.py` would be caching search results so that similar labels would not be submitted multiple times.* 

*The OLS search may be retrieving proper mappings for* Lentivirus.human-immunodeficiency-virus1 (Human immunodeficiency virus 1, NCBITaxon:11676) *and* Nepovirus.Tobacco-ringspot-virus (Tobacco ringspot virus, NCBITaxon:12282), *but terms that combine a genus and a species are handled in any special way, so that is a vulnerability at this time.*

*In the default configuration,* Simian virus 40 *is incorrectly mapped to* Simian virus 41, NCBITaxon:2560766. NCBITaxon:1891767 'Macaca mulatta polyomavirus 1' is probably the correct mapping, with equivalent name 'Simian virus 40'. NCBITaxon:10633 is an alternative ID. I have not found any configuration of `webmap_enums.py` to retrieve the correct term for this string.

*In the default configuration, no acceptable mappings are found for the following. (The same iterative approach can help here, too.)*

- '#N/A'

  - *No NCBItaxon mapping expected.*

- 'Saccharomyces cerevisiae/Bacillus subtilis/Bacillus subtilis'

  - *Multiple taxa in input. No NCBItaxon mapping expected.*

- 'herpes.simplex.virus-1'

  - NCBITaxon:10298 'Human alphaherpesvirus 1' *has the related genbank synonym* 'Herpes simplex virus 1' *and can be found  by prioritizing non-label annotations with the modification* `--query_fields annotations,label`

- 'Human influenza hemagglutinin'

  - *Taxon + protein. No NCBItaxon mapping expected*

- 'NA'

  - *No NCBItaxon mapping expected.*

- 'phage.lambda'

  - NCBITaxon:10710 *has the label* Escherichia virus Lambda. 'Phage lambda' *or* 'lambda phage' *are assigned to several different synonyms and annotations. This hit can be retrieved by prioritizing annotations hits over label hits with* `--query_fields annotations,label`.

- 'Pseudomonas plasmid pVS1'

  - *The default search retrieves* NCBITaxon:219557, *labeled* 'Plasmid pVS1'. *No other relevant annotations are available, so the word 'Pseudomonas' becomes noise in the string distance calculation. Perhaps a string distance metric other than cosine would help?*

- 'SARS-CoV-2'

  - NCBITaxon:2697049 *has the label* Severe acute respiratory syndrome coronavirus 2 *and the genbank acronym* 'SARS-CoV-2'. *This hit can be retrieved by prioritizing annotations hits over label hits with* `--query_fields annotations,label` *and by disabling the substitution of whitespace for hyphens with something like* `--replaced_chars ._` 

    

**Add Sequence Ontology mappings on top of the NCBItaxon mappings**

```bash
./linkml_model_enrichment/enum_annotator.py \
--verbosity DEBUG \
--modelfile target/ncbitaxon_mappings.yaml \
--tabular_outputfile target/ncbi_so_mappings_log.tsv \
--ontoprefix so \
--enum_list Engineering_enum \
--search_engine OLS > target/ncbi_so_mappings.yaml
```



**Add ENVO mappings for MIxS soil types**

```bash
./linkml_model_enrichment/enum_annotator.py \
--verbosity DEBUG \
--modelfile target/ncbi_so_mappings.yaml \
--tabular_outputfile target/ncbi_so__envo_mappings.tsv \
--ontoprefix envo \
--enum_list FAO_enum \
--search_engine OLS > target/ncbi_so__envo_mappings.yaml
```



### Options

```bash
enum_annotator.py [OPTIONS]

  Uses web-based ontology lookup tools to map the permitted values of enums
  from linkml files to CURIES. Optionally overwrites the meaning with a
  CURIE and the description with a preferred label. Writes the resulting
  YAML to STDOUT.

Options:
  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  -f, --modelfile PATH            Path to a YAML linkml file containing
                                  enumerated values.  [required]

  -t, --tabular_outputfile PATH   A tsv dump of all search results will be
                                  written to this file.  [default:
                                  mappings_log.tsv]

  -p, --ontoprefix TEXT           comma-separated list of (abbreviated)
                                  ontologies to search over.  [default:
                                  NCBITaxon,SO,ENVO,PATO,GO,OBI]

  -e, --enum_list TEXT            Comma-separated list of enums to search
                                  with. Defaults to all enums.

  -q, --query_fields TEXT         Comma-separated list of term properties to
                                  include in string similarity calculation.
                                  Defaults to label,synonym,description,short_
                                  form,obo_id,annotations,logical_description,
                                  iri.

  -c, --replaced_chars TEXT       Characters to replace with whitespace.
                                  [default: \.\_\- ]

  -n, --min_search_chars INTEGER  TEMPORARILY DISABLED. Queries with fewer
                                  characters will not be submitted in the
                                  search.  [default: 2]

  -r, --row_req INTEGER           Requested number of search results.
                                  [default: 5]

  -x, --maxdist FLOAT             Maximum string distance between query and
                                  best matching term's best matching property.
                                  [default: 0.05]

  -m, --overwite_meaning          Should existing enum meanings and
                                  descriptions be overwritten?

  -s, --search_engine TEXT        BioPortal option has been temporarily
                                  disabled.  [default: OLS]

  --help                          Show this message and exit.
```
