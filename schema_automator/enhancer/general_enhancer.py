import re
import logging
from dataclasses import dataclass
from typing import List, Callable

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, ClassDefinitionName, SlotDefinition


@dataclass
class GeneralSchemaEnhancer:
    """
    Multiple methods for adding additional information to schemas
    """

    def add_titles(self, schema: SchemaDefinition):
        """
        Add titles to all elements if not present

        :param schema: input schema, will be modified in place
        :return:
        """
        sv = SchemaView(schema)
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        for e in sv.all_elements():
            if e.title is not None:
                continue
            title = e.name.replace('_', ' ')
            title = pattern.sub(' ', title).lower()
            e.title = title


    def add_container(self, schema: SchemaDefinition, class_name: str = 'Container',
                      force: bool = False) -> ClassDefinition:
        """
        Adds a container class

        :param schema: input schema, will be modified in place
        :param class_name:
        :param force:
        :return: container class
        """
        sv = SchemaView(schema)
        tree_roots = [for c in sv.all_classes().values() if c.tree_root]
        if len(tree_roots) > 0:
            if force:
                logging.info(f'Forcing addition of containers')
            else:
                raise ValueError(f'Schema already has containers: {tree_roots}')
        container = ClassDefinition(class_name, tree_root=True)
        sv.add_class(container)
        self.add_index_slots(container.name)
        return container


    def add_index_slots(self, schema: SchemaDefinition, container_name: ClassDefinitionName, inlined_as_list = False,
                        must_have_identifier = False, slot_name_func: Callable = None) -> List[SlotDefinition]:
        """
        Adds index slots to a container pointing at all top-level classes

        :param schema: input schema, will be modified in place
        :param container_name:
        :param inlined_as_list:
        :param must_have_identifier:
        :param slot_name_func: function to determine the name of the slot from the class
        :return: new slots
        """
        sv = SchemaView(schema)
        container = sv.get_class(container_name)
        ranges = set()
        for cn in sv.all_classes():
            for s in sv.class_induced_slots(cn):
                ranges.add(s.range)
        top_level_classes = [c for c in sv.all_classes().values() if not c.tree_root and c.name not in ranges]
        if must_have_identifier:
            top_level_classes = [c for c in top_level_classes if sv.get_identifier_slot(c.name) is not None]
        index_slots = []
        for c in top_level_classes:
            has_identifier = sv.get_identifier_slot(c.name)
            if slot_name_func:
                sn = slot_name_func(c)
            else:
                sn = f'{c.name}_index'
            index_slot = SlotDefinition(sn,
                                        range=c.name,
                                        multivalued=True,
                                        inlined_as_list=not has_identifier or inlined_as_list)
            index_slots.append(index_slot)
            container.slots.append(index_slot.name)
        return index_slots

    def attributes_to_slots(self, schema: SchemaDefinition):
        sv = SchemaView(schema)
        new_slots = []
        for c in sv.all_classes().values():
            for a in c.attributes:
                new_slots.append(a)
            self.merge_slot_usage(sv, c, a)
            c.attributes = {}
        for slot in new_slots:
            if slot.name in sv.all_slots():
                raise ValueError(f'Duplicate slot {slot.name}')
            sv.add_slot(slot)
        self.remove_redundant_slot_usage(schema)

    def merge_slot_usage(self, sv: SchemaView, cls: ClassDefinition, slot: SlotDefinition):
        if slot.name not in cls.slot_usage:
            cls.slot_usage[slot.name] = slot
        else:
            su = cls.slot_usage[slot.name]
            for k, v in vars(slot).items():
                curr_v = getattr(su, k, None)
                if curr_v and curr_v != v:
                    raise ValueError(f'Conflict in {cls.name}.{slot.name}, attr {k} {v} != {curr_v}')
                setattr(su, k, v)

    def remove_redundant_slot_usage(self, schema: SchemaDefinition):
        sv = SchemaView(schema)
        # TODO






