import logging
from copy import copy
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Union, Optional

import click
from linkml.generators.pythongen import PythonGenerator
from linkml.utils import datautils
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import ClassDefinitionName, SlotDefinitionName
from linkml_runtime.utils.yamlutils import YAMLRoot

ID_REF = str
PATH = List[str]


@dataclass
class InstanceView:
    """
    A wrapper over an instance and it's sub-instances (instance tree)
    """
    root: YAMLRoot = None
    schemaview: SchemaView = None
    id_to_path: Dict[ID_REF, PATH] = field(default_factory=lambda: {})
    id_to_obj: Dict[ID_REF, YAMLRoot] = field(default_factory=lambda: {})
    references: List[Tuple[ID_REF, ID_REF]] = field(default_factory=lambda: [])

    def create_index(self, obj: Union[YAMLRoot, Dict, List] = None,
                     path=None, parent=None):
        """
        Creates internal index

        :param obj:
        :param path:
        :param parent:
        :return:
        """
        logging.debug(f'Creating index...')
        if path is None:
            path = []
        if obj is None:
            obj = self.root
        sv = self.schemaview
        indent = len(path) * '    '
        #print(f'{indent}{type(obj)} // {path}')
        if isinstance(obj, dict):
            for k, v in obj.items():
                self.create_index(v, path=path + [k], parent=parent)
        elif isinstance(obj, list):
            for i in range(0, len(obj)-1):
                self.create_index(obj[i], path=path + [i], parent=parent)
        elif isinstance(obj, YAMLRoot):
            cn = type(obj).class_name
            for slot in sv.class_induced_slots(cn):
                v = getattr(obj, slot.alias, None)
                if v is not None:
                    if slot.identifier:
                        self.references.append((parent, v))
                        # TODO: use explicit scheme to prioritize
                        if v not in self.id_to_path:
                            self.id_to_path[v] = path
                            self.id_to_obj[v] = obj
                        else:
                            curr_path = self.id_to_path[v]
                            if len(path) < len(curr_path):
                                self.id_to_path[v] = path
                                self.id_to_obj[v] = obj
                    else:
                        if slot.range in sv.all_classes():
                            if isinstance(v, str):
                                self.references.append((parent, v))
                        self.create_index(v, path=path+[slot.alias], parent=obj)
        logging.debug(f'Created index')

    def fetch_object(self, id_ref: ID_REF, default_val = None) -> Optional[YAMLRoot]:
        """
        Fetches an object by ID

        :param id_ref:
        :param default_val:
        :return: default_val if ID is dangling, otherwise return object with that ID
        """
        return self.id_to_obj.get(id_ref, default_val)


    def extract(self, seeds: List[ID_REF], preserve_slots: List[SlotDefinitionName] = None) -> YAMLRoot:
        """
        Extracts a subtree using a seed set of identifiers

        The subtree will include ancestors and descendants of identifiers, plus all recursive
        subtrees of all referenced entities

        :param seeds:
        :param preserve_slots:
        :return:
        """
        logging.info(f'Extracting from seed: {seeds}')
        id_to_path = self.id_to_path
        xdict = {}
        to_visit = copy(seeds)
        visited = set()
        while len(to_visit) > 0:
            nxt = to_visit.pop()
            if nxt in visited:
                continue
            logging.info(f'Extracting: {nxt}; {len(to_visit)} to go')
            if nxt not in id_to_path:
                logging.warning(f'No element with ID {nxt}')
                continue
            obj = self.fetch_object(nxt)
            path = self.id_to_path[nxt][0:-1]
            if len(path) != 1:
                continue
                #raise ValueError(f'{path} for {nxt}')
            #print(f'{nxt} = {rg} // {type(obj)}')
            islot = path[0]
            if islot not in xdict:
                if isinstance(getattr(self.root, islot), dict):
                    xdict[islot] = {}
                else:
                    xdict[islot] = []
            if isinstance(xdict[islot], dict):
                xdict[islot][nxt] = obj
            else:
                xdict[islot].append(obj)
            refs = self.get_object_references(obj)
            for ref in refs:
                if ref not in visited:
                    to_visit.append(ref)
            visited.add(nxt)
        if preserve_slots is None:
            preserve_slots = []
        root_cls = type(self.root)
        for slot in self.schemaview.class_induced_slots(root_cls.class_name):
            if slot.required:
                preserve_slots.append(slot.alias)
        for slot in preserve_slots:
            xdict[slot] = getattr(self.root, slot)
        #print(f'VISITED={visited}')
        #print(yaml_dumper.dumps(xdict))
        return root_cls(**xdict)


    def get_object_references(self, start_obj: Optional[Union[YAMLRoot, Dict, List]],
                              depth: int = 0) -> List[ID_REF]:
        logging.info(f'Fetching object references from {type(start_obj)}')
        if object is None:
            return []
        sv = self.schemaview
        refs = []
        indent = '    ' * depth
        #print(f'{indent}IN {type(obj)}')
        seeds = [start_obj]
        visited = set()
        while len(seeds) > 0:
            obj = seeds.pop()
            if isinstance(obj, YAMLRoot):
                for slot in sv.class_induced_slots(type(obj).class_name):
                    v = getattr(obj, slot.alias, None)
                    if v is not None:
                        if slot.identifier:
                            refs.append(v)
                        else:
                            rg = slot.range
                            if rg in sv.all_classes():
                                #print(f'{indent} - OBJ {type(obj)} {slot.alias} = {v} // {rg} // cumul={refs}')
                                if isinstance(v, list):
                                    seeds += v
                                elif isinstance(v, dict):
                                    seeds += v.values()
                                else:
                                    seeds.append(v)
            else:
                if obj not in visited:
                    refs.append(obj)
                    if obj in self.id_to_obj:
                        seeds.append(self.id_to_obj[obj])
                    visited.add(obj)
        #print(f'{indent}OUT {type(obj)} {cn} = {refs}')
        return list(set(refs))



@click.command()
@click.argument('elements', nargs=-1)
@click.option('--schema', '-s', help="Schema file")
@click.option('--input', '-i', help="Data input")
@click.option('--output', '-o', help="Path to saved yaml schema")
def cli(elements, input, schema, output, **args):
    """
    Extract from instance data
    """
    sv = SchemaView(schema)
    fmt = datautils._get_format(input)
    loader = datautils.get_loader(fmt)
    python_module = PythonGenerator(schema).compile_module()
    target_class = datautils.infer_root_class(sv)
    py_target_class = python_module.__dict__[target_class]
    root = loader.load(source=input,  target_class=py_target_class,)
    iv = InstanceView(root=root, schemaview=sv)
    iv.extract(elements)

if __name__ == '__main__':
    cli()



