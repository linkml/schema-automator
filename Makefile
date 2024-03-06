RUN = poetry run
VERSION = $(shell git tag | tail -1)
MODELS = cadsr frictionless

.PHONY: all clean test all-docs sphinx-html

all: clean test


test:
	$(RUN) pytest tests/

schema_automator/metamodels/%.py: schema_automator/metamodels/%.yaml
	$(RUN) gen-python $< > $@.tmp && mv $@.tmp $@


# create a convenient wrapper script;
# this can be used outside the poetry environment
bin/schemauto:
	echo `poetry run which schemauto` '"$$@"' > $@ && chmod +x $@

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

################################################
#### Commands for building the Docker image ####
################################################

IM=linkml/schema-automator

docker-build-no-cache:
	@docker build --no-cache -t $(IM):$(VERSION) . \
	&& docker tag $(IM):$(VERSION) $(IM):latest

docker-build:
	@docker build -t $(IM):$(VERSION) . \
	&& docker tag $(IM):$(VERSION) $(IM):latest

docker-build-use-cache-dev:
	@docker build -t $(DEV):$(VERSION) . \
	&& docker tag $(DEV):$(VERSION) $(DEV):latest

docker-clean:
	docker kill $(IM) || echo not running ;
	docker rm $(IM) || echo not made 

docker-publish-no-build:
	@docker push $(IM):$(VERSION) \
	&& docker push $(IM):latest

docker-publish-dev-no-build:
	@docker push $(DEV):$(VERSION) \
	&& docker push $(DEV):latest

docker-publish: docker-build
	@docker push $(IM):$(VERSION) \
	&& docker push $(IM):latest

docker-run:
	@docker run  -v $(PWD):/work -w /work -ti $(IM):$(VERSION) 
