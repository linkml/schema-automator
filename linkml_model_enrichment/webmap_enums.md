# `webmap_enums.py` documentation



`webmap_enums.py` reads the lables of the enums in a linkml model and submits them to a web-based term mapping service. Rudimentary code for using the BioPortal annotator has been commented out as the OLS term search has be emphasized in recent develoment effort.

 All of the mappings are written to a TSV (`mappings_log.tsv` by default) file specified by `--tabular_outputfile`

The enums' descriptions and meanings can be poverwritten if the following two conditions are true:

- If the cosine distance between the enum's label and the best search result's label or synonyms is less than or equal to the treshold (`--maxdist`, 0.05)
- If there was no meaning in the input, or if the `--overwite_meaning` is set

The model is written out to `STDOUT`, whether any enums ahve been updated or not.

`webmap_enums.py` should be executed from the `linkml-model-enrichment` repo's root directory. The input files mentioned in the examples below are not guaranteed to be present in a cloned `linkml-model-enrichment` repo.

**Map taxon-related enums from the IARPA Synthetic Biology project to NCBItaxon terms, without overwriting anything**

```bash
./linkml_model_enrichment/webmap_enums.py \     
--verbosity DEBUG \
--modelfile target/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml \
--tabular_outputfile synbio_ncbitaxon_mappings_log.tsv \
--ontoprefix ncbitaxon \
--enum_list host_organism_enum,species_enum \
--search_engine OLS > synbio_ncbitaxon_mappings.yaml
```

*That takes 4 minutes on a 2020 Intel MacBook Pro with a 200 MB/s network connection. `webmap_enums.py` has not been optimized for speed in any way. The greatest time cost appears to come from waiting for responses from the search engine. The BioPortal annotator indicates the what portion of the enum label was matched to which property of the matched terms by default, but retireiving the same information from OLS requires retreiving details for each matched term. One example of a potential improvement to `webmap_enums.py` would be caching search results so that similar labels would not be submitted miltiple times.* 

*The OLS search may be retrieving proper mapings for* Lentivirus.human-immunodeficiency-virus1 (Human immunodeficiency virus 1, NCBITaxon:11676) *and* Nepovirus.Tobacco-ringspot-virus (Tobacco ringspot virus, NCBITaxon:12282), *but terms that combine a genus and a species are handled in any special way, so that is a vilnerability at this time.*

*In the default configuration,* Simian virus 40 *is incorrectly mapped to* Simian virus 41, NCBITaxon:2560766. Changes to the `--enum_list` and  `--query_fields` arguments can result in better mappings for some terms, but degraded mappings for others. In this case, multiple iterations of `webmap_enums.py` can be run in the default no-overwrite mode.

*In the default configuration, no acceptable mapings are found for the following. (The same iterative approach can help here, too.)*

- '#N/A'
  - *No NCBItaxon mapping expected.*
- 'Saccharomyces cerevisiae/Bacillus subtilis/Bacillus subtilis'
  - *Multiple taxa. No NCBItaxon mapping expected.*
- **'herpes.simplex.virus-1'**
- 'Human influenza hemagglutinin'
  - *Taxon + protein. No NCBItaxon mapping expected*
- 'NA'
  - *No NCBItaxon mapping expected.*
- **'phage.lambda'**
- 'Pseudomonas plasmid pVS1'
  - *The default search retrives* NCBITaxon:219557, *labeled* 'Plasmid pVS1'. *No other relavant annotations are available, so the word 'Pseudomonas' becomes noise in the string distance calculation. Perhaps a string distance metric other than cosine would help?*
- **'SARS-CoV-2'**
  - *The default search substitites hypens (among other characters) for whitespace. With that subsitution,* Severe acute respiratory syndrome coronavirus 2, NCBITaxon:2697049 *is just not retrieved*.

**Add Sequence Ontology mappings on top of the IARPA Synthetic Biology NCBItaxon mappings**

```bash
./linkml_model_enrichment/webmap_enums.py \
--verbosity DEBUG \
--modelfile synbio_ncbitaxon_mappings.yaml \
--tabular_outputfile synbio_ncbi_so_mappings_log.tsv \
--ontoprefix so \
--enum_list type_enum,type_long_enum \
--search_engine OLS > synbio_ncbi_so_mappings.yaml
```



```bash
./linkml_model_enrichment/webmap_enums.py \
--verbosity DEBUG \
--modelfile ../biosample-analysis/gensc.github.io/src/schema/mixs.yaml \
--tabular_outputfile mixs_5_fao_envo_mappings_log.tsv \
--ontoprefix envo \
--enum_list fao_class_enum \
--search_engine OLS > mixs_5_fao_envo_mappings.yaml
```



### Options

```bash
webmap_enums.py [OPTIONS]

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



