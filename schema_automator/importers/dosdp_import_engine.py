from copy import deepcopy

import click
import logging
import yaml
from typing import Union, Dict, Tuple, List, Any
from collections import defaultdict
import os
from csv import DictWriter

from dataclasses import dataclass

from linkml_runtime.linkml_model.meta import SchemaDefinition, ClassDefinition, SlotDefinition, EnumDefinition, TypeDefinition, AnonymousSlotExpression
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.formatutils import camelcase, underscore

from schema_automator.importers.import_engine import ImportEngine
from schema_automator.dosdp.model import Pattern, Printf
from schema_automator.utils.schemautils import write_schema

ALIAS = str
CURIE = str

METACLASS = 'OntologyClass'
TEMPLATE_CLASS = 'OntologyClassTemplate'
GROUPING_CLASS = 'OntologyClassSubset'

@dataclass
class DOSDPImportEngine(ImportEngine):
    """
    An ImportEngine that imports Ontology Design Patterns specified as DOSDP Yaml into a LinkML schema

    See `DOSDPs <https://github.com/INCATools/dead_simple_owl_design_patterns>`_

    Every template maps to a LinkML class, the default name for a template Foo as FooTemplate

    """
    mappings: dict = None
    include_unmapped_annotations = False

    def load_dp(self, path) -> Pattern:
        with open(path) as stream:
            obj = yaml.safe_load(stream)
        if 'def' in obj:
            obj['definition'] = obj['def']
            del obj['def']
        return yaml_loader.load(obj, target_class=Pattern)

    def convert(self, files: str, range_as_enums = True, **kwargs) -> SchemaDefinition:
        """
        Converts one or more YAML files into a Schema

        :param files:
        :param range_as_enums: if True, then class ranges are mapped to Enums
        :param kwargs:
        :return:
        """
        patterns = [self.load_dp(file) for file in files]
        schema = SchemaDefinition(**kwargs)
        if not schema.default_prefix:
            schema.default_prefix = schema.name
            schema.prefixes[schema.name] = f'{schema.id}'
        schema.default_curi_maps = ['semweb_context', 'obo_context']
        self.schema = schema
        mc = ClassDefinition(METACLASS)
        schema.classes[mc.name] = mc
        mc.description = "Instance of OWL Class"
        mc.aliases = ['OWL Class']
        mc.class_uri = 'owl:Class'
        mc.mixin = True
        mc.slots = ['id']
        tmc = ClassDefinition(TEMPLATE_CLASS)
        schema.classes[tmc.name] = tmc
        tmc.description = "Instances of OWL classes that conform to a template"
        tmc.aliases = ['design pattern record', 'template row']
        tmc.mixin = True
        tmc.mixins = [mc.name]
        gmc = ClassDefinition(GROUPING_CLASS)
        schema.classes[gmc.name] = gmc
        gmc.description = "Mixin for instances of OWL Classes that are used as range references"
        gmc.mixin = True
        gmc.mixins = [mc.name]
        schema.types['string'] = TypeDefinition(name='string', base='str', uri='xsd:string')
        def add_slot(s: SlotDefinition):
            schema.slots[s.name] = s
        add_slot(SlotDefinition('id',
                                identifier=True,
                                #range='uriorcurie',
                                description='Unique identifier for template instance'))
        add_slot(SlotDefinition('name',
                                slot_uri='rdfs:label',
                                description='Human readable label for template instance'))
        add_slot(SlotDefinition('definition',
                                slot_uri='IAO:0000115',
                                description='Human readable textual definition for template instance'))
        add_slot(SlotDefinition('subclass_of',
                                multivalued=True,
                                slot_uri='rdfs:subclass_of',
                                range=METACLASS))
        add_slot(SlotDefinition('equivalentTo',
                                description='String serialization of RHS expression in equivalence axiom',
                                close_mappings=['owl:equivalentClass']))
        licenses = set()
        for p in patterns:
            c = self.create_class(p, range_as_enums=range_as_enums)
            schema.classes[c.name] = c
        return schema

    def create_class(self, pattern: Pattern, range_as_enums: bool = True,
                     denormalize_labels: bool = True) -> ClassDefinition:
        """
        Create a LinkML class from a template/pattern

        The class will have name FooTemplate, and will mixin TemplateClass,
        and will have one slot per var (slots will also be inherited from TemplateClass)

        by default, the range of each var will be a class RangeClass, unless treated as enums

        :param pattern: DOSDP template
        :param range_as_enums:  if true, ranges will be enums
        :param denoramlized:  if true, create an optional label for each var
        :return:
        """
        def deref_class(name: ALIAS) -> CURIE:
            return self._deref(name, pattern.classes)

        schema = self.schema
        template_name = f'{pattern.pattern_name} template'
        cls = ClassDefinition(name=camelcase(template_name),
                              aliases=[template_name],
                              #title=template_name,  ## TODO: fix owlgen
                              description=pattern.description,
                              mixins=[TEMPLATE_CLASS])
        for contrib in pattern.contributors:
            cls.comments.append(f'Contributor: {contrib}')  ## TODO: extend metamodel
        extra_classes = []
        for vn, v in pattern.vars.items():
            var_range_as_curie = v.range
            for alias, alias_obj in pattern.classes.items():
                if f"'{alias}'" == v.range:
                    var_range_as_curie = alias_obj.curie
            range_base_name = self._name(v.range)
            if range_as_enums:
                rangedef = self.create_enum(f'{range_base_name} enum')
            else:
                rangedef = ClassDefinition(camelcase(f'{range_base_name} class'))
                #rangedef.is_a = METACLASS
                rangedef.mixins = [GROUPING_CLASS]
                subc_slot = SlotDefinition('subclass_of',
                                           has_member=AnonymousSlotExpression(equals_string=var_range_as_curie))
                rangedef.slot_usage[subc_slot.name] = subc_slot
                extra_classes.append(rangedef)
            rangedef.description = f'Any subclass of {var_range_as_curie} ({v.range})'
            slot = SlotDefinition(vn, range=rangedef.name)
            schema.slots[slot.name] = slot
            cls.slots.append(slot.name)
            cls.slot_usage[slot.name] = slot
            if denormalize_labels:
                label_slot = SlotDefinition(f'{vn}_label',
                                            description=f'label for {vn}',
                                            string_serialization=f'{{{vn}}}.label')
                schema.slots[label_slot.name] = label_slot
                cls.slots.append(label_slot.name)
                cls.slot_usage[label_slot.name] = label_slot
        # populate metaclass
        mc = schema.classes[METACLASS]

        for k in ['name', 'definition', 'equivalentTo']:
            pf = getattr(pattern, k)
            #print(f'k={k} rule={srule}')
            if pf is not None:
                slot = self._serialization_slot(k, pf)
                if slot.name not in mc.slots:
                    mc.slots.append(slot.name)
                    #schema.slots[slot.name] = deepcopy(slot)
                    #schema.slots[slot.name].string_serialization = None
                cls.slot_usage[slot.name] = slot
        # append these at the end
        for c in extra_classes:
            schema.classes[c.name] = c
        return cls

    def create_enum(self, name: str):
        name = underscore(self._name(name))
        enumdef = EnumDefinition(name)
        self.schema.enums[enumdef.name] = enumdef
        return enumdef


    def _serialization_slot(self, k: str, pf: Printf):
        slot = SlotDefinition(k)
        t = pf.text
        for vn in pf.vars:
            t = t.replace('%', f'{{{vn}}}', 1)
        slot.string_serialization = t
        return slot

    def _name(self, name: ALIAS) -> ALIAS:
        if name.startswith("'"):
            name = name.replace("'","")
        return name

    def _deref(self, name: ALIAS, index: dict) -> CURIE:
        if name.startswith("'"):
            name = name.replace("'","")
            return index[name].curie


@click.command()
@click.argument('dpfiles', nargs=-1) ## input DOSDPs
@click.option('--name', '-n', help="Schema name")
@click.option('--range-as-enum/--no-range-as-enums', default=True, help="Model range ontology classes as enyms")
@click.option('--output', '-o', help="Path to saved yaml schema")
def dosdp2model(dpfiles, output, **args):
    """
    Infer a model from DOSDP

    """
    ie = DOSDPImportEngine()
    schema = ie.convert(dpfiles, **args)
    write_schema(schema, output)

if __name__ == '__main__':
    dosdp2model()


