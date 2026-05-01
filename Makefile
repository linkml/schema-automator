RUN = uv run
MODELS = cadsr frictionless

.PHONY: all clean test all-docs sphinx-html check-dependencies

all: clean test


test:
	$(RUN) pytest tests/

schema_automator/metamodels/%.py: schema_automator/metamodels/%.yaml
	$(RUN) gen-python $< > $@.tmp && mv $@.tmp $@

check-dependencies:
	$(RUN) deptry schema_automator --known-first-party schema_automator

########################
#### Metamodel docs ####
########################

all-docs: $(patsubst %,docs-%,$(MODELS))

docs-dosdp: schema_automator/metamodels/dosdp/dosdp_linkml.yaml
	$(RUN) gen-doc -d docs/metamodels/dosdp $<

docs-%: schema_automator/metamodels/%.yaml
	$(RUN) gen-doc -d docs/metamodels/$* $<

sphinx-%:
	cd docs && $(RUN) make $*
.PHONY: sphinx-%
