import click
import logging
import yaml
from typing import Union, Dict, Tuple, List, Any
from collections import defaultdict
import os
from csv import DictWriter

from dataclasses import dataclass

from linkml_runtime.linkml_model.meta import SchemaDefinition, ClassDefinition, SlotDefinition, EnumDefinition, TypeDefinition
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.formatutils import camelcase, underscore

from linkml_model_enrichment.importers.import_engine import ImportEngine
from linkml_model_enrichment.dosdp.model import Pattern, Printf

ALIAS = str
CURIE = str

METACLASS = 'Metaclass'

@dataclass
class DOSDPImportEngine(ImportEngine):
    mappings: dict = None
    include_unmapped_annotations = False

    def load_dp(self, path) -> Pattern:
        with open(path) as stream:
            obj = yaml.safe_load(stream)
        if 'def' in obj:
            obj['definition'] = obj['def']
            del obj['def']
        return yaml_loader.load(obj, target_class=Pattern)

    def convert(self, files: str, **kwargs) -> SchemaDefinition:
        patterns = [self.load_dp(file) for file in files]
        schema = SchemaDefinition(**kwargs)
        schema.default_prefix = schema.name
        schema.prefixes[schema.name] = f'https://example.org/{schema.name}'
        self.schema = schema
        schema.classes[METACLASS] = ClassDefinition(METACLASS)
        schema.types['string'] = TypeDefinition(name='string', base='str', uri='xsd:string')
        for p in patterns:
            c = self.create_class(p)
            schema.classes[c.name] = c
        return schema

    def create_class(self, pattern: Pattern) -> ClassDefinition:
        def deref_class(name: ALIAS) -> CURIE:
            return self._deref(name, pattern.classes)

        schema = self.schema
        cls = ClassDefinition(name=camelcase(pattern.pattern_name),
                              description=pattern.description,
                              is_a=METACLASS)
        for vn, v in pattern.vars.items():
            enumdef = self.create_enum(v.range)
            slot = SlotDefinition(vn, range=enumdef.name)
            schema.slots[slot.name] = slot
            cls.slots.append(slot.name)
            cls.slot_usage[slot.name] = slot
        mc = schema.classes[METACLASS]
        for k in ['name', 'definition', 'equivalentTo']:
            pf = getattr(pattern, k)
            #print(f'k={k} rule={srule}')
            if pf is not None:
                slot = self._serialization_slot(k, pf)
                if slot.name not in mc.slots:
                    mc.slots.append(slot.name)
                    schema.slots[slot.name] = slot
                cls.slot_usage[slot.name] = slot

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
@click.option('--output', '-o', help="Path to saved yaml schema")
def dosdp2model(dpfiles, output, **args):
    """
    Infer a model from DOSDP

    """
    ie = DOSDPImportEngine()
    schema = ie.convert(dpfiles, **args)
    ys = yaml.dump(schema, default_flow_style=False, sort_keys=False)
    if output:
        with open(output, 'w') as stream:
            stream.write(ys)
    else:
        print(ys)

if __name__ == '__main__':
    dosdp2model()


