# Auto generated from frictionless.yaml by pythongen.py version: 0.9.0
# Generation date: 2022-07-08T14:42:16
# Schema: frictionless
#
# id: https://w3id.org/linkml/frictionless
# description: frictionless
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Boolean, String
from linkml_runtime.utils.metamodelcore import Bool

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
ANY = CurieNamespace('Any', 'http://example.org/UNKNOWN/Any/')
FRICTIONLESS = CurieNamespace('frictionless', 'https://w3id.org/linkml/frictionless/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = FRICTIONLESS


# Types

# Class references
class FieldName(extended_str):
    pass


class ResourceName(extended_str):
    pass


class PackageName(extended_str):
    pass


Any = Any

@dataclass
class Dialect(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Dialect
    class_class_curie: ClassVar[str] = "frictionless:Dialect"
    class_name: ClassVar[str] = "Dialect"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Dialect

    delimiter: Optional[str] = None
    doubleQuote: Optional[Union[bool, Bool]] = None
    lineTerminator: Optional[str] = None
    skipInitialSpace: Optional[Union[bool, Bool]] = None
    header: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.delimiter is not None and not isinstance(self.delimiter, str):
            self.delimiter = str(self.delimiter)

        if self.doubleQuote is not None and not isinstance(self.doubleQuote, Bool):
            self.doubleQuote = Bool(self.doubleQuote)

        if self.lineTerminator is not None and not isinstance(self.lineTerminator, str):
            self.lineTerminator = str(self.lineTerminator)

        if self.skipInitialSpace is not None and not isinstance(self.skipInitialSpace, Bool):
            self.skipInitialSpace = Bool(self.skipInitialSpace)

        if self.header is not None and not isinstance(self.header, Bool):
            self.header = Bool(self.header)

        super().__post_init__(**kwargs)


@dataclass
class Constraints(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Constraints
    class_class_curie: ClassVar[str] = "frictionless:Constraints"
    class_name: ClassVar[str] = "Constraints"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Constraints

    required: Optional[Union[bool, Bool]] = None
    pattern: Optional[str] = None
    unique: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.required is not None and not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if self.pattern is not None and not isinstance(self.pattern, str):
            self.pattern = str(self.pattern)

        if self.unique is not None and not isinstance(self.unique, Bool):
            self.unique = Bool(self.unique)

        super().__post_init__(**kwargs)


@dataclass
class Field(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Field
    class_class_curie: ClassVar[str] = "frictionless:Field"
    class_name: ClassVar[str] = "Field"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Field

    name: Union[str, FieldName] = None
    description: Optional[Union[str, List[str]]] = empty_list()
    type: Optional[Union[str, "TypeEnum"]] = None
    constraints: Optional[Union[dict, Constraints]] = None
    format: Optional[Union[str, "FormatEnum"]] = None
    enum: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, FieldName):
            self.name = FieldName(self.name)

        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if self.type is not None and not isinstance(self.type, TypeEnum):
            self.type = TypeEnum(self.type)

        if self.constraints is not None and not isinstance(self.constraints, Constraints):
            self.constraints = Constraints(**as_dict(self.constraints))

        if self.format is not None and not isinstance(self.format, FormatEnum):
            self.format = FormatEnum(self.format)

        if not isinstance(self.enum, list):
            self.enum = [self.enum] if self.enum is not None else []
        self.enum = [v if isinstance(v, str) else str(v) for v in self.enum]

        super().__post_init__(**kwargs)


@dataclass
class Reference(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Reference
    class_class_curie: ClassVar[str] = "frictionless:Reference"
    class_name: ClassVar[str] = "Reference"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Reference

    resource: Optional[str] = None
    fields: Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]] = empty_list()
    range: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.resource is not None and not isinstance(self.resource, str):
            self.resource = str(self.resource)

        if not isinstance(self.fields, list):
            self.fields = [self.fields] if self.fields is not None else []
        self.fields = [v if isinstance(v, FieldName) else FieldName(v) for v in self.fields]

        if self.range is not None and not isinstance(self.range, str):
            self.range = str(self.range)

        super().__post_init__(**kwargs)


@dataclass
class ForeignKeys(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.ForeignKeys
    class_class_curie: ClassVar[str] = "frictionless:ForeignKeys"
    class_name: ClassVar[str] = "ForeignKeys"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.ForeignKeys

    fields: Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]] = empty_list()
    reference: Optional[Union[dict, Reference]] = None
    constraint_name: Optional[str] = None
    range: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.fields, list):
            self.fields = [self.fields] if self.fields is not None else []
        self.fields = [v if isinstance(v, FieldName) else FieldName(v) for v in self.fields]

        if self.reference is not None and not isinstance(self.reference, Reference):
            self.reference = Reference(**as_dict(self.reference))

        if self.constraint_name is not None and not isinstance(self.constraint_name, str):
            self.constraint_name = str(self.constraint_name)

        if self.range is not None and not isinstance(self.range, str):
            self.range = str(self.range)

        super().__post_init__(**kwargs)


@dataclass
class Schema(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Schema
    class_class_curie: ClassVar[str] = "frictionless:Schema"
    class_name: ClassVar[str] = "Schema"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Schema

    fields: Optional[Union[Dict[Union[str, FieldName], Union[dict, Field]], List[Union[dict, Field]]]] = empty_dict()
    missingValues: Optional[Union[str, List[str]]] = empty_list()
    primaryKey: Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]] = empty_list()
    foreignKeys: Optional[Union[Union[dict, ForeignKeys], List[Union[dict, ForeignKeys]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="fields", slot_type=Field, key_name="name", keyed=True)

        if not isinstance(self.missingValues, list):
            self.missingValues = [self.missingValues] if self.missingValues is not None else []
        self.missingValues = [v if isinstance(v, str) else str(v) for v in self.missingValues]

        if not isinstance(self.primaryKey, list):
            self.primaryKey = [self.primaryKey] if self.primaryKey is not None else []
        self.primaryKey = [v if isinstance(v, FieldName) else FieldName(v) for v in self.primaryKey]

        if not isinstance(self.foreignKeys, list):
            self.foreignKeys = [self.foreignKeys] if self.foreignKeys is not None else []
        self.foreignKeys = [v if isinstance(v, ForeignKeys) else ForeignKeys(**as_dict(v)) for v in self.foreignKeys]

        super().__post_init__(**kwargs)


@dataclass
class Resource(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Resource
    class_class_curie: ClassVar[str] = "frictionless:Resource"
    class_name: ClassVar[str] = "Resource"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Resource

    name: Union[str, ResourceName] = None
    profile: Optional[Union[str, "ProfileEnum"]] = None
    title: Optional[str] = None
    path: Optional[str] = None
    dialect: Optional[str] = None
    description: Optional[Union[str, List[str]]] = empty_list()
    schema: Optional[Union[dict, Schema]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, ResourceName):
            self.name = ResourceName(self.name)

        if self.profile is not None and not isinstance(self.profile, ProfileEnum):
            self.profile = ProfileEnum(self.profile)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.path is not None and not isinstance(self.path, str):
            self.path = str(self.path)

        if self.dialect is not None and not isinstance(self.dialect, str):
            self.dialect = str(self.dialect)

        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if self.schema is not None and not isinstance(self.schema, Schema):
            self.schema = Schema(**as_dict(self.schema))

        super().__post_init__(**kwargs)


@dataclass
class Package(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FRICTIONLESS.Package
    class_class_curie: ClassVar[str] = "frictionless:Package"
    class_name: ClassVar[str] = "Package"
    class_model_uri: ClassVar[URIRef] = FRICTIONLESS.Package

    name: Union[str, PackageName] = None
    profile: Optional[Union[str, "ProfileEnum"]] = None
    title: Optional[str] = None
    resources: Optional[Union[Dict[Union[str, ResourceName], Union[dict, Resource]], List[Union[dict, Resource]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, PackageName):
            self.name = PackageName(self.name)

        if self.profile is not None and not isinstance(self.profile, ProfileEnum):
            self.profile = ProfileEnum(self.profile)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        self._normalize_inlined_as_list(slot_name="resources", slot_type=Resource, key_name="name", keyed=True)

        super().__post_init__(**kwargs)


# Enumerations
class TypeEnum(EnumDefinitionImpl):

    string = PermissibleValue(text="string",
                                   description="string")
    datetime = PermissibleValue(text="datetime",
                                       description="datetime")
    boolean = PermissibleValue(text="boolean",
                                     description="boolean")
    integer = PermissibleValue(text="integer",
                                     description="integer")
    array = PermissibleValue(text="array",
                                 description="array")
    number = PermissibleValue(text="number",
                                   description="number")

    _defn = EnumDefinition(
        name="TypeEnum",
    )

class FormatEnum(EnumDefinitionImpl):

    any = PermissibleValue(text="any",
                             description="any")
    email = PermissibleValue(text="email",
                                 description="email")
    binary = PermissibleValue(text="binary",
                                   description="binary")

    _defn = EnumDefinition(
        name="FormatEnum",
    )

class ProfileEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="ProfileEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "tabular-data-resource",
                PermissibleValue(text="tabular-data-resource") )
        setattr(cls, "tabular-data-package",
                PermissibleValue(text="tabular-data-package") )

# Slots
class slots:
    pass

slots.delimiter = Slot(uri=FRICTIONLESS.delimiter, name="delimiter", curie=FRICTIONLESS.curie('delimiter'),
                   model_uri=FRICTIONLESS.delimiter, domain=None, range=Optional[str])

slots.doubleQuote = Slot(uri=FRICTIONLESS.doubleQuote, name="doubleQuote", curie=FRICTIONLESS.curie('doubleQuote'),
                   model_uri=FRICTIONLESS.doubleQuote, domain=None, range=Optional[Union[bool, Bool]])

slots.lineTerminator = Slot(uri=FRICTIONLESS.lineTerminator, name="lineTerminator", curie=FRICTIONLESS.curie('lineTerminator'),
                   model_uri=FRICTIONLESS.lineTerminator, domain=None, range=Optional[str])

slots.skipInitialSpace = Slot(uri=FRICTIONLESS.skipInitialSpace, name="skipInitialSpace", curie=FRICTIONLESS.curie('skipInitialSpace'),
                   model_uri=FRICTIONLESS.skipInitialSpace, domain=None, range=Optional[Union[bool, Bool]])

slots.header = Slot(uri=FRICTIONLESS.header, name="header", curie=FRICTIONLESS.curie('header'),
                   model_uri=FRICTIONLESS.header, domain=None, range=Optional[Union[bool, Bool]])

slots.required = Slot(uri=LINKML.required, name="required", curie=LINKML.curie('required'),
                   model_uri=FRICTIONLESS.required, domain=None, range=Optional[Union[bool, Bool]])

slots.pattern = Slot(uri=LINKML.pattern, name="pattern", curie=LINKML.curie('pattern'),
                   model_uri=FRICTIONLESS.pattern, domain=None, range=Optional[str])

slots.unique = Slot(uri=LINKML.identifier, name="unique", curie=LINKML.curie('identifier'),
                   model_uri=FRICTIONLESS.unique, domain=None, range=Optional[Union[bool, Bool]])

slots.name = Slot(uri=LINKML.name, name="name", curie=LINKML.curie('name'),
                   model_uri=FRICTIONLESS.name, domain=None, range=URIRef)

slots.description = Slot(uri=LINKML.description, name="description", curie=LINKML.curie('description'),
                   model_uri=FRICTIONLESS.description, domain=None, range=Optional[Union[str, List[str]]])

slots.type = Slot(uri=FRICTIONLESS.type, name="type", curie=FRICTIONLESS.curie('type'),
                   model_uri=FRICTIONLESS.type, domain=None, range=Optional[Union[str, "TypeEnum"]])

slots.constraints = Slot(uri=FRICTIONLESS.constraints, name="constraints", curie=FRICTIONLESS.curie('constraints'),
                   model_uri=FRICTIONLESS.constraints, domain=None, range=Optional[Union[dict, Constraints]])

slots.format = Slot(uri=FRICTIONLESS.format, name="format", curie=FRICTIONLESS.curie('format'),
                   model_uri=FRICTIONLESS.format, domain=None, range=Optional[Union[str, "FormatEnum"]])

slots.enum = Slot(uri=FRICTIONLESS.enum, name="enum", curie=FRICTIONLESS.curie('enum'),
                   model_uri=FRICTIONLESS.enum, domain=None, range=Optional[Union[str, List[str]]])

slots.resource = Slot(uri=FRICTIONLESS.resource, name="resource", curie=FRICTIONLESS.curie('resource'),
                   model_uri=FRICTIONLESS.resource, domain=None, range=Optional[str])

slots.fields = Slot(uri=FRICTIONLESS.fields, name="fields", curie=FRICTIONLESS.curie('fields'),
                   model_uri=FRICTIONLESS.fields, domain=None, range=Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]])

slots.reference = Slot(uri=FRICTIONLESS.reference, name="reference", curie=FRICTIONLESS.curie('reference'),
                   model_uri=FRICTIONLESS.reference, domain=None, range=Optional[Union[dict, Reference]])

slots.constraint_name = Slot(uri=FRICTIONLESS.constraint_name, name="constraint_name", curie=FRICTIONLESS.curie('constraint_name'),
                   model_uri=FRICTIONLESS.constraint_name, domain=None, range=Optional[str])

slots.missingValues = Slot(uri=FRICTIONLESS.missingValues, name="missingValues", curie=FRICTIONLESS.curie('missingValues'),
                   model_uri=FRICTIONLESS.missingValues, domain=None, range=Optional[Union[str, List[str]]])

slots.primaryKey = Slot(uri=FRICTIONLESS.primaryKey, name="primaryKey", curie=FRICTIONLESS.curie('primaryKey'),
                   model_uri=FRICTIONLESS.primaryKey, domain=None, range=Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]])

slots.foreignKeys = Slot(uri=FRICTIONLESS.foreignKeys, name="foreignKeys", curie=FRICTIONLESS.curie('foreignKeys'),
                   model_uri=FRICTIONLESS.foreignKeys, domain=None, range=Optional[Union[Union[dict, ForeignKeys], List[Union[dict, ForeignKeys]]]])

slots.profile = Slot(uri=FRICTIONLESS.profile, name="profile", curie=FRICTIONLESS.curie('profile'),
                   model_uri=FRICTIONLESS.profile, domain=None, range=Optional[Union[str, "ProfileEnum"]])

slots.title = Slot(uri=LINKML.title, name="title", curie=LINKML.curie('title'),
                   model_uri=FRICTIONLESS.title, domain=None, range=Optional[str])

slots.path = Slot(uri=FRICTIONLESS.path, name="path", curie=FRICTIONLESS.curie('path'),
                   model_uri=FRICTIONLESS.path, domain=None, range=Optional[str])

slots.dialect = Slot(uri=FRICTIONLESS.dialect, name="dialect", curie=FRICTIONLESS.curie('dialect'),
                   model_uri=FRICTIONLESS.dialect, domain=None, range=Optional[str])

slots.schema = Slot(uri=FRICTIONLESS.schema, name="schema", curie=FRICTIONLESS.curie('schema'),
                   model_uri=FRICTIONLESS.schema, domain=None, range=Optional[Union[dict, Schema]])

slots.resources = Slot(uri=FRICTIONLESS.resources, name="resources", curie=FRICTIONLESS.curie('resources'),
                   model_uri=FRICTIONLESS.resources, domain=None, range=Optional[Union[Dict[Union[str, ResourceName], Union[dict, Resource]], List[Union[dict, Resource]]]])

slots.range = Slot(uri=FRICTIONLESS.range, name="range", curie=FRICTIONLESS.curie('range'),
                   model_uri=FRICTIONLESS.range, domain=None, range=Optional[str])

slots.Reference_fields = Slot(uri=FRICTIONLESS.fields, name="Reference_fields", curie=FRICTIONLESS.curie('fields'),
                   model_uri=FRICTIONLESS.Reference_fields, domain=Reference, range=Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]])

slots.Reference_range = Slot(uri=FRICTIONLESS.range, name="Reference_range", curie=FRICTIONLESS.curie('range'),
                   model_uri=FRICTIONLESS.Reference_range, domain=Reference, range=Optional[str])

slots.ForeignKeys_fields = Slot(uri=FRICTIONLESS.fields, name="ForeignKeys_fields", curie=FRICTIONLESS.curie('fields'),
                   model_uri=FRICTIONLESS.ForeignKeys_fields, domain=ForeignKeys, range=Optional[Union[Union[str, FieldName], List[Union[str, FieldName]]]])

slots.ForeignKeys_range = Slot(uri=FRICTIONLESS.range, name="ForeignKeys_range", curie=FRICTIONLESS.curie('range'),
                   model_uri=FRICTIONLESS.ForeignKeys_range, domain=ForeignKeys, range=Optional[str])

slots.Schema_fields = Slot(uri=FRICTIONLESS.fields, name="Schema_fields", curie=FRICTIONLESS.curie('fields'),
                   model_uri=FRICTIONLESS.Schema_fields, domain=Schema, range=Optional[Union[Dict[Union[str, FieldName], Union[dict, Field]], List[Union[dict, Field]]]])
