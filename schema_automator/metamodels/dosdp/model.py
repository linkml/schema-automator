# Auto generated from dosdp_linkml.yaml by pythongen.py version: 0.9.0
# Generation date: 2021-08-31 01:14
# Schema: DOSDP
#
# id: https://w3id.org/linkml/dosdp
# description:
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

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
DOSDP = CurieNamespace('dosdp', 'https://w3id.org/linkml/dosdp/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DOSDP


# Types

# Class references
class VarDeclarationVar(extended_str):
    pass


class AliasDeclarationAlias(extended_str):
    pass


@dataclass
class Pattern(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Pattern
    class_class_curie: ClassVar[str] = "dosdp:Pattern"
    class_name: ClassVar[str] = "Pattern"
    class_model_uri: ClassVar[URIRef] = DOSDP.Pattern

    pattern_name: Optional[str] = None
    pattern_iri: Optional[str] = None
    base_IRI: Optional[str] = None
    contributors: Optional[Union[str, List[str]]] = empty_list()
    description: Optional[str] = None
    examples: Optional[str] = None
    status: Optional[Union[str, "StatusOptions"]] = None
    tags: Optional[str] = None
    readable_identifiers: Optional[Union[str, List[str]]] = empty_list()
    classes: Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]] = empty_dict()
    objectProperties: Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]] = empty_dict()
    relations: Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]] = empty_dict()
    dataProperties: Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]] = empty_dict()
    annotationProperties: Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]] = empty_dict()
    vars: Optional[Union[Dict[Union[str, VarDeclarationVar], Union[dict, "VarDeclaration"]], List[Union[dict, "VarDeclaration"]]]] = empty_dict()
    list_vars: Optional[str] = None
    data_vars: Optional[str] = None
    data_list_vars: Optional[str] = None
    internal_vars: Optional[Union[str, List[str]]] = empty_list()
    substitutions: Optional[Union[Union[dict, "RegexSub"], List[Union[dict, "RegexSub"]]]] = empty_list()
    annotations: Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]] = empty_list()
    logical_axioms: Optional[Union[Union[dict, "PrintfOwl"], List[Union[dict, "PrintfOwl"]]]] = empty_list()
    equivalentTo: Optional[Union[dict, "PrintfOwlConvenience"]] = None
    subClassOf: Optional[Union[dict, "PrintfOwlConvenience"]] = None
    GCI: Optional[Union[dict, "PrintfOwlConvenience"]] = None
    disjointWith: Optional[Union[dict, "PrintfOwlConvenience"]] = None
    name: Optional[Union[dict, "PrintfAnnotationObo"]] = None
    comment: Optional[Union[dict, "PrintfAnnotationObo"]] = None
    definition: Optional[Union[dict, "PrintfAnnotationObo"]] = None
    namespace: Optional[Union[dict, "PrintfAnnotationObo"]] = None
    exact_synonym: Optional[Union[dict, "ListAnnotationObo"]] = None
    narrow_synonym: Optional[Union[dict, "ListAnnotationObo"]] = None
    related_synonym: Optional[Union[dict, "ListAnnotationObo"]] = None
    broad_synonym: Optional[Union[dict, "ListAnnotationObo"]] = None
    xref: Optional[Union[dict, "ListAnnotationObo"]] = None
    generated_synonyms: Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]] = empty_list()
    generated_narrow_synonyms: Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]] = empty_list()
    generated_broad_synonyms: Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]] = empty_list()
    generated_related_synonyms: Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]] = empty_list()
    instance_graph: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.pattern_name is not None and not isinstance(self.pattern_name, str):
            self.pattern_name = str(self.pattern_name)

        if self.pattern_iri is not None and not isinstance(self.pattern_iri, str):
            self.pattern_iri = str(self.pattern_iri)

        if self.base_IRI is not None and not isinstance(self.base_IRI, str):
            self.base_IRI = str(self.base_IRI)

        if not isinstance(self.contributors, list):
            self.contributors = [self.contributors] if self.contributors is not None else []
        self.contributors = [v if isinstance(v, str) else str(v) for v in self.contributors]

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.examples is not None and not isinstance(self.examples, str):
            self.examples = str(self.examples)

        if self.status is not None and not isinstance(self.status, StatusOptions):
            self.status = StatusOptions(self.status)

        if self.tags is not None and not isinstance(self.tags, str):
            self.tags = str(self.tags)

        if not isinstance(self.readable_identifiers, list):
            self.readable_identifiers = [self.readable_identifiers] if self.readable_identifiers is not None else []
        self.readable_identifiers = [v if isinstance(v, str) else str(v) for v in self.readable_identifiers]

        self._normalize_inlined_as_dict(slot_name="classes", slot_type=AliasDeclaration, key_name="alias", keyed=True)

        self._normalize_inlined_as_dict(slot_name="objectProperties", slot_type=AliasDeclaration, key_name="alias", keyed=True)

        self._normalize_inlined_as_dict(slot_name="relations", slot_type=AliasDeclaration, key_name="alias", keyed=True)

        self._normalize_inlined_as_dict(slot_name="dataProperties", slot_type=AliasDeclaration, key_name="alias", keyed=True)

        self._normalize_inlined_as_dict(slot_name="annotationProperties", slot_type=AliasDeclaration, key_name="alias", keyed=True)

        self._normalize_inlined_as_dict(slot_name="vars", slot_type=VarDeclaration, key_name="var", keyed=True)

        if self.list_vars is not None and not isinstance(self.list_vars, str):
            self.list_vars = str(self.list_vars)

        if self.data_vars is not None and not isinstance(self.data_vars, str):
            self.data_vars = str(self.data_vars)

        if self.data_list_vars is not None and not isinstance(self.data_list_vars, str):
            self.data_list_vars = str(self.data_list_vars)

        if not isinstance(self.internal_vars, list):
            self.internal_vars = [self.internal_vars] if self.internal_vars is not None else []
        self.internal_vars = [v if isinstance(v, str) else str(v) for v in self.internal_vars]

        self._normalize_inlined_as_dict(slot_name="substitutions", slot_type=RegexSub, key_name="out", keyed=False)

        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if not isinstance(self.logical_axioms, list):
            self.logical_axioms = [self.logical_axioms] if self.logical_axioms is not None else []
        self.logical_axioms = [v if isinstance(v, PrintfOwl) else PrintfOwl(**as_dict(v)) for v in self.logical_axioms]

        if self.equivalentTo is not None and not isinstance(self.equivalentTo, PrintfOwlConvenience):
            self.equivalentTo = PrintfOwlConvenience(**as_dict(self.equivalentTo))

        if self.subClassOf is not None and not isinstance(self.subClassOf, PrintfOwlConvenience):
            self.subClassOf = PrintfOwlConvenience(**as_dict(self.subClassOf))

        if self.GCI is not None and not isinstance(self.GCI, PrintfOwlConvenience):
            self.GCI = PrintfOwlConvenience(**as_dict(self.GCI))

        if self.disjointWith is not None and not isinstance(self.disjointWith, PrintfOwlConvenience):
            self.disjointWith = PrintfOwlConvenience(**as_dict(self.disjointWith))

        if self.name is not None and not isinstance(self.name, PrintfAnnotationObo):
            self.name = PrintfAnnotationObo(**as_dict(self.name))

        if self.comment is not None and not isinstance(self.comment, PrintfAnnotationObo):
            self.comment = PrintfAnnotationObo(**as_dict(self.comment))

        if self.definition is not None and not isinstance(self.definition, PrintfAnnotationObo):
            self.definition = PrintfAnnotationObo(**as_dict(self.definition))

        if self.namespace is not None and not isinstance(self.namespace, PrintfAnnotationObo):
            self.namespace = PrintfAnnotationObo(**as_dict(self.namespace))

        if self.exact_synonym is not None and not isinstance(self.exact_synonym, ListAnnotationObo):
            self.exact_synonym = ListAnnotationObo(**as_dict(self.exact_synonym))

        if self.narrow_synonym is not None and not isinstance(self.narrow_synonym, ListAnnotationObo):
            self.narrow_synonym = ListAnnotationObo(**as_dict(self.narrow_synonym))

        if self.related_synonym is not None and not isinstance(self.related_synonym, ListAnnotationObo):
            self.related_synonym = ListAnnotationObo(**as_dict(self.related_synonym))

        if self.broad_synonym is not None and not isinstance(self.broad_synonym, ListAnnotationObo):
            self.broad_synonym = ListAnnotationObo(**as_dict(self.broad_synonym))

        if self.xref is not None and not isinstance(self.xref, ListAnnotationObo):
            self.xref = ListAnnotationObo(**as_dict(self.xref))

        if not isinstance(self.generated_synonyms, list):
            self.generated_synonyms = [self.generated_synonyms] if self.generated_synonyms is not None else []
        self.generated_synonyms = [v if isinstance(v, PrintfAnnotationObo) else PrintfAnnotationObo(**as_dict(v)) for v in self.generated_synonyms]

        if not isinstance(self.generated_narrow_synonyms, list):
            self.generated_narrow_synonyms = [self.generated_narrow_synonyms] if self.generated_narrow_synonyms is not None else []
        self.generated_narrow_synonyms = [v if isinstance(v, PrintfAnnotationObo) else PrintfAnnotationObo(**as_dict(v)) for v in self.generated_narrow_synonyms]

        if not isinstance(self.generated_broad_synonyms, list):
            self.generated_broad_synonyms = [self.generated_broad_synonyms] if self.generated_broad_synonyms is not None else []
        self.generated_broad_synonyms = [v if isinstance(v, PrintfAnnotationObo) else PrintfAnnotationObo(**as_dict(v)) for v in self.generated_broad_synonyms]

        if not isinstance(self.generated_related_synonyms, list):
            self.generated_related_synonyms = [self.generated_related_synonyms] if self.generated_related_synonyms is not None else []
        self.generated_related_synonyms = [v if isinstance(v, PrintfAnnotationObo) else PrintfAnnotationObo(**as_dict(v)) for v in self.generated_related_synonyms]

        if self.instance_graph is not None and not isinstance(self.instance_graph, str):
            self.instance_graph = str(self.instance_graph)

        super().__post_init__(**kwargs)


class Declaration(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Declaration
    class_class_curie: ClassVar[str] = "dosdp:Declaration"
    class_name: ClassVar[str] = "Declaration"
    class_model_uri: ClassVar[URIRef] = DOSDP.Declaration


@dataclass
class VarDeclaration(Declaration):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.VarDeclaration
    class_class_curie: ClassVar[str] = "dosdp:VarDeclaration"
    class_name: ClassVar[str] = "VarDeclaration"
    class_model_uri: ClassVar[URIRef] = DOSDP.VarDeclaration

    var: Union[str, VarDeclarationVar] = None
    range: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.var):
            self.MissingRequiredField("var")
        if not isinstance(self.var, VarDeclarationVar):
            self.var = VarDeclarationVar(self.var)

        if self.range is not None and not isinstance(self.range, str):
            self.range = str(self.range)

        super().__post_init__(**kwargs)


@dataclass
class AliasDeclaration(Declaration):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.AliasDeclaration
    class_class_curie: ClassVar[str] = "dosdp:AliasDeclaration"
    class_name: ClassVar[str] = "AliasDeclaration"
    class_model_uri: ClassVar[URIRef] = DOSDP.AliasDeclaration

    alias: Union[str, AliasDeclarationAlias] = None
    curie: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.alias):
            self.MissingRequiredField("alias")
        if not isinstance(self.alias, AliasDeclarationAlias):
            self.alias = AliasDeclarationAlias(self.alias)

        if self.curie is not None and not isinstance(self.curie, str):
            self.curie = str(self.curie)

        super().__post_init__(**kwargs)


@dataclass
class MultiClausePrintf(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.MultiClausePrintf
    class_class_curie: ClassVar[str] = "dosdp:MultiClausePrintf"
    class_name: ClassVar[str] = "MultiClausePrintf"
    class_model_uri: ClassVar[URIRef] = DOSDP.MultiClausePrintf

    clauses: Union[Union[dict, "PrintfClause"], List[Union[dict, "PrintfClause"]]] = None
    sep: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.clauses):
            self.MissingRequiredField("clauses")
        self._normalize_inlined_as_dict(slot_name="clauses", slot_type=PrintfClause, key_name="text", keyed=False)

        if self.sep is not None and not isinstance(self.sep, str):
            self.sep = str(self.sep)

        super().__post_init__(**kwargs)


@dataclass
class PrintfClause(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.PrintfClause
    class_class_curie: ClassVar[str] = "dosdp:PrintfClause"
    class_name: ClassVar[str] = "PrintfClause"
    class_model_uri: ClassVar[URIRef] = DOSDP.PrintfClause

    text: str = None
    vars: Union[str, List[str]] = None
    sub_clauses: Optional[Union[Union[dict, MultiClausePrintf], List[Union[dict, MultiClausePrintf]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.text):
            self.MissingRequiredField("text")
        if not isinstance(self.text, str):
            self.text = str(self.text)

        if self._is_empty(self.vars):
            self.MissingRequiredField("vars")
        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        self._normalize_inlined_as_dict(slot_name="sub_clauses", slot_type=MultiClausePrintf, key_name="clauses", keyed=False)

        super().__post_init__(**kwargs)


class Function(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Function
    class_class_curie: ClassVar[str] = "dosdp:Function"
    class_name: ClassVar[str] = "Function"
    class_model_uri: ClassVar[URIRef] = DOSDP.Function


@dataclass
class Join(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Join
    class_class_curie: ClassVar[str] = "dosdp:Join"
    class_name: ClassVar[str] = "Join"
    class_model_uri: ClassVar[URIRef] = DOSDP.Join

    sep: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.sep is not None and not isinstance(self.sep, str):
            self.sep = str(self.sep)

        super().__post_init__(**kwargs)


@dataclass
class PrintfAnnotation(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.PrintfAnnotation
    class_class_curie: ClassVar[str] = "dosdp:PrintfAnnotation"
    class_name: ClassVar[str] = "PrintfAnnotation"
    class_model_uri: ClassVar[URIRef] = DOSDP.PrintfAnnotation

    annotationProperty: str = None
    annotations: Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]] = empty_list()
    text: Optional[str] = None
    vars: Optional[Union[str, List[str]]] = empty_list()
    multi_clause: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.annotationProperty):
            self.MissingRequiredField("annotationProperty")
        if not isinstance(self.annotationProperty, str):
            self.annotationProperty = str(self.annotationProperty)

        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if self.text is not None and not isinstance(self.text, str):
            self.text = str(self.text)

        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        if self.multi_clause is not None and not isinstance(self.multi_clause, str):
            self.multi_clause = str(self.multi_clause)

        super().__post_init__(**kwargs)


@dataclass
class ListAnnotation(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.ListAnnotation
    class_class_curie: ClassVar[str] = "dosdp:ListAnnotation"
    class_name: ClassVar[str] = "ListAnnotation"
    class_model_uri: ClassVar[URIRef] = DOSDP.ListAnnotation

    annotationProperty: str = None
    value: str = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.annotationProperty):
            self.MissingRequiredField("annotationProperty")
        if not isinstance(self.annotationProperty, str):
            self.annotationProperty = str(self.annotationProperty)

        if self._is_empty(self.value):
            self.MissingRequiredField("value")
        if not isinstance(self.value, str):
            self.value = str(self.value)

        super().__post_init__(**kwargs)


@dataclass
class IriValueAnnotation(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.IriValueAnnotation
    class_class_curie: ClassVar[str] = "dosdp:IriValueAnnotation"
    class_name: ClassVar[str] = "IriValueAnnotation"
    class_model_uri: ClassVar[URIRef] = DOSDP.IriValueAnnotation

    annotationProperty: str = None
    var: str = None
    annotations: Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.annotationProperty):
            self.MissingRequiredField("annotationProperty")
        if not isinstance(self.annotationProperty, str):
            self.annotationProperty = str(self.annotationProperty)

        if self._is_empty(self.var):
            self.MissingRequiredField("var")
        if not isinstance(self.var, str):
            self.var = str(self.var)

        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        super().__post_init__(**kwargs)


class Annotation(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Annotation
    class_class_curie: ClassVar[str] = "dosdp:Annotation"
    class_name: ClassVar[str] = "Annotation"
    class_model_uri: ClassVar[URIRef] = DOSDP.Annotation


@dataclass
class Printf(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.Printf
    class_class_curie: ClassVar[str] = "dosdp:Printf"
    class_name: ClassVar[str] = "Printf"
    class_model_uri: ClassVar[URIRef] = DOSDP.Printf

    text: Optional[str] = None
    vars: Optional[Union[str, List[str]]] = empty_list()
    annotations: Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.text is not None and not isinstance(self.text, str):
            self.text = str(self.text)

        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        super().__post_init__(**kwargs)


@dataclass
class PrintfOwl(Printf):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.PrintfOwl
    class_class_curie: ClassVar[str] = "dosdp:PrintfOwl"
    class_name: ClassVar[str] = "PrintfOwl"
    class_model_uri: ClassVar[URIRef] = DOSDP.PrintfOwl

    annotations: Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]] = empty_list()
    axiom_type: Optional[Union[str, "AxiomTypeOptions"]] = None
    text: Optional[str] = None
    vars: Optional[Union[str, List[str]]] = empty_list()
    multi_clause: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if self.axiom_type is not None and not isinstance(self.axiom_type, AxiomTypeOptions):
            self.axiom_type = AxiomTypeOptions(self.axiom_type)

        if self.text is not None and not isinstance(self.text, str):
            self.text = str(self.text)

        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        if self.multi_clause is not None and not isinstance(self.multi_clause, str):
            self.multi_clause = str(self.multi_clause)

        super().__post_init__(**kwargs)


@dataclass
class PrintfOwlConvenience(Printf):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.PrintfOwlConvenience
    class_class_curie: ClassVar[str] = "dosdp:PrintfOwlConvenience"
    class_name: ClassVar[str] = "PrintfOwlConvenience"
    class_model_uri: ClassVar[URIRef] = DOSDP.PrintfOwlConvenience

    annotations: Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]] = empty_list()
    text: Optional[str] = None
    vars: Optional[Union[str, List[str]]] = empty_list()
    multi_clause: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if self.text is not None and not isinstance(self.text, str):
            self.text = str(self.text)

        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        if self.multi_clause is not None and not isinstance(self.multi_clause, str):
            self.multi_clause = str(self.multi_clause)

        super().__post_init__(**kwargs)


@dataclass
class RegexSub(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.RegexSub
    class_class_curie: ClassVar[str] = "dosdp:RegexSub"
    class_name: ClassVar[str] = "RegexSub"
    class_model_uri: ClassVar[URIRef] = DOSDP.RegexSub

    out: str = None
    match: str = None
    sub: str = None
    _in: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.out):
            self.MissingRequiredField("out")
        if not isinstance(self.out, str):
            self.out = str(self.out)

        if self._is_empty(self.match):
            self.MissingRequiredField("match")
        if not isinstance(self.match, str):
            self.match = str(self.match)

        if self._is_empty(self.sub):
            self.MissingRequiredField("sub")
        if not isinstance(self.sub, str):
            self.sub = str(self.sub)

        if self._in is not None and not isinstance(self._in, str):
            self._in = str(self._in)

        super().__post_init__(**kwargs)


@dataclass
class OPA(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.OPA
    class_class_curie: ClassVar[str] = "dosdp:OPA"
    class_name: ClassVar[str] = "OPA"
    class_model_uri: ClassVar[URIRef] = DOSDP.OPA

    edge: Union[str, List[str]] = None
    annotations: Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]] = empty_list()
    _not: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.edge):
            self.MissingRequiredField("edge")
        if not isinstance(self.edge, list):
            self.edge = [self.edge] if self.edge is not None else []
        self.edge = [v if isinstance(v, str) else str(v) for v in self.edge]

        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if self._not is not None and not isinstance(self._not, Bool):
            self._not = Bool(self._not)

        super().__post_init__(**kwargs)


@dataclass
class PrintfAnnotationObo(Printf):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.PrintfAnnotationObo
    class_class_curie: ClassVar[str] = "dosdp:PrintfAnnotationObo"
    class_name: ClassVar[str] = "PrintfAnnotationObo"
    class_model_uri: ClassVar[URIRef] = DOSDP.PrintfAnnotationObo

    annotations: Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]] = empty_list()
    xrefs: Optional[str] = None
    text: Optional[str] = None
    vars: Optional[Union[str, List[str]]] = empty_list()
    multi_clause: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.annotations, list):
            self.annotations = [self.annotations] if self.annotations is not None else []
        self.annotations = [v if isinstance(v, Annotation) else Annotation(**as_dict(v)) for v in self.annotations]

        if self.xrefs is not None and not isinstance(self.xrefs, str):
            self.xrefs = str(self.xrefs)

        if self.text is not None and not isinstance(self.text, str):
            self.text = str(self.text)

        if not isinstance(self.vars, list):
            self.vars = [self.vars] if self.vars is not None else []
        self.vars = [v if isinstance(v, str) else str(v) for v in self.vars]

        if self.multi_clause is not None and not isinstance(self.multi_clause, str):
            self.multi_clause = str(self.multi_clause)

        super().__post_init__(**kwargs)


@dataclass
class ListAnnotationObo(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DOSDP.ListAnnotationObo
    class_class_curie: ClassVar[str] = "dosdp:ListAnnotationObo"
    class_name: ClassVar[str] = "ListAnnotationObo"
    class_model_uri: ClassVar[URIRef] = DOSDP.ListAnnotationObo

    value: str = None
    xrefs: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.value):
            self.MissingRequiredField("value")
        if not isinstance(self.value, str):
            self.value = str(self.value)

        if self.xrefs is not None and not isinstance(self.xrefs, str):
            self.xrefs = str(self.xrefs)

        super().__post_init__(**kwargs)


# Enumerations
class AxiomTypeOptions(EnumDefinitionImpl):

    equivalentTo = PermissibleValue(text="equivalentTo")
    subClassOf = PermissibleValue(text="subClassOf")
    disjointWith = PermissibleValue(text="disjointWith")
    GCI = PermissibleValue(text="GCI")

    _defn = EnumDefinition(
        name="AxiomTypeOptions",
    )

class StatusOptions(EnumDefinitionImpl):

    development = PermissibleValue(text="development")
    published = PermissibleValue(text="published")

    _defn = EnumDefinition(
        name="StatusOptions",
    )

# Slots
class slots:
    pass

slots.sep = Slot(uri=DOSDP.sep, name="sep", curie=DOSDP.curie('sep'),
                   model_uri=DOSDP.sep, domain=None, range=Optional[str])

slots.clauses = Slot(uri=DOSDP.clauses, name="clauses", curie=DOSDP.curie('clauses'),
                   model_uri=DOSDP.clauses, domain=None, range=Union[Union[dict, PrintfClause], List[Union[dict, PrintfClause]]])

slots.text = Slot(uri=DOSDP.text, name="text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.text, domain=None, range=Optional[str])

slots.vars = Slot(uri=DOSDP.vars, name="vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.vars, domain=None, range=Optional[Union[str, List[str]]])

slots.sub_clauses = Slot(uri=DOSDP.sub_clauses, name="sub_clauses", curie=DOSDP.curie('sub_clauses'),
                   model_uri=DOSDP.sub_clauses, domain=None, range=Optional[Union[Union[dict, MultiClausePrintf], List[Union[dict, MultiClausePrintf]]]])

slots.annotationProperty = Slot(uri=DOSDP.annotationProperty, name="annotationProperty", curie=DOSDP.curie('annotationProperty'),
                   model_uri=DOSDP.annotationProperty, domain=None, range=str)

slots.annotations = Slot(uri=DOSDP.annotations, name="annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.annotations, domain=None, range=Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]])

slots.multi_clause = Slot(uri=DOSDP.multi_clause, name="multi_clause", curie=DOSDP.curie('multi_clause'),
                   model_uri=DOSDP.multi_clause, domain=None, range=Optional[str])

slots.value = Slot(uri=DOSDP.value, name="value", curie=DOSDP.curie('value'),
                   model_uri=DOSDP.value, domain=None, range=str)

slots.var = Slot(uri=DOSDP.var, name="var", curie=DOSDP.curie('var'),
                   model_uri=DOSDP.var, domain=None, range=str)

slots.axiom_type = Slot(uri=DOSDP.axiom_type, name="axiom_type", curie=DOSDP.curie('axiom_type'),
                   model_uri=DOSDP.axiom_type, domain=None, range=Optional[Union[str, "AxiomTypeOptions"]])

slots._in = Slot(uri=DOSDP._in, name="_in", curie=DOSDP.curie('_in'),
                   model_uri=DOSDP._in, domain=None, range=Optional[str])

slots.out = Slot(uri=DOSDP.out, name="out", curie=DOSDP.curie('out'),
                   model_uri=DOSDP.out, domain=None, range=str)

slots.match = Slot(uri=DOSDP.match, name="match", curie=DOSDP.curie('match'),
                   model_uri=DOSDP.match, domain=None, range=str)

slots.sub = Slot(uri=DOSDP.sub, name="sub", curie=DOSDP.curie('sub'),
                   model_uri=DOSDP.sub, domain=None, range=str)

slots.edge = Slot(uri=DOSDP.edge, name="edge", curie=DOSDP.curie('edge'),
                   model_uri=DOSDP.edge, domain=None, range=Union[str, List[str]])

slots._not = Slot(uri=DOSDP._not, name="_not", curie=DOSDP.curie('_not'),
                   model_uri=DOSDP._not, domain=None, range=Optional[Union[bool, Bool]])

slots.xrefs = Slot(uri=DOSDP.xrefs, name="xrefs", curie=DOSDP.curie('xrefs'),
                   model_uri=DOSDP.xrefs, domain=None, range=Optional[str])

slots.pattern_name = Slot(uri=DOSDP.pattern_name, name="pattern_name", curie=DOSDP.curie('pattern_name'),
                   model_uri=DOSDP.pattern_name, domain=None, range=Optional[str])

slots.pattern_iri = Slot(uri=DOSDP.pattern_iri, name="pattern_iri", curie=DOSDP.curie('pattern_iri'),
                   model_uri=DOSDP.pattern_iri, domain=None, range=Optional[str])

slots.base_IRI = Slot(uri=DOSDP.base_IRI, name="base_IRI", curie=DOSDP.curie('base_IRI'),
                   model_uri=DOSDP.base_IRI, domain=None, range=Optional[str])

slots.contributors = Slot(uri=DOSDP.contributors, name="contributors", curie=DOSDP.curie('contributors'),
                   model_uri=DOSDP.contributors, domain=None, range=Optional[Union[str, List[str]]])

slots.description = Slot(uri=DOSDP.description, name="description", curie=DOSDP.curie('description'),
                   model_uri=DOSDP.description, domain=None, range=Optional[str])

slots.examples = Slot(uri=DOSDP.examples, name="examples", curie=DOSDP.curie('examples'),
                   model_uri=DOSDP.examples, domain=None, range=Optional[str])

slots.status = Slot(uri=DOSDP.status, name="status", curie=DOSDP.curie('status'),
                   model_uri=DOSDP.status, domain=None, range=Optional[Union[str, "StatusOptions"]])

slots.tags = Slot(uri=DOSDP.tags, name="tags", curie=DOSDP.curie('tags'),
                   model_uri=DOSDP.tags, domain=None, range=Optional[str])

slots.readable_identifiers = Slot(uri=DOSDP.readable_identifiers, name="readable_identifiers", curie=DOSDP.curie('readable_identifiers'),
                   model_uri=DOSDP.readable_identifiers, domain=None, range=Optional[Union[str, List[str]]])

slots.classes = Slot(uri=DOSDP.classes, name="classes", curie=DOSDP.curie('classes'),
                   model_uri=DOSDP.classes, domain=None, range=Optional[str])

slots.objectProperties = Slot(uri=DOSDP.objectProperties, name="objectProperties", curie=DOSDP.curie('objectProperties'),
                   model_uri=DOSDP.objectProperties, domain=None, range=Optional[str])

slots.relations = Slot(uri=DOSDP.relations, name="relations", curie=DOSDP.curie('relations'),
                   model_uri=DOSDP.relations, domain=None, range=Optional[str])

slots.dataProperties = Slot(uri=DOSDP.dataProperties, name="dataProperties", curie=DOSDP.curie('dataProperties'),
                   model_uri=DOSDP.dataProperties, domain=None, range=Optional[str])

slots.annotationProperties = Slot(uri=DOSDP.annotationProperties, name="annotationProperties", curie=DOSDP.curie('annotationProperties'),
                   model_uri=DOSDP.annotationProperties, domain=None, range=Optional[str])

slots.list_vars = Slot(uri=DOSDP.list_vars, name="list_vars", curie=DOSDP.curie('list_vars'),
                   model_uri=DOSDP.list_vars, domain=None, range=Optional[str])

slots.data_vars = Slot(uri=DOSDP.data_vars, name="data_vars", curie=DOSDP.curie('data_vars'),
                   model_uri=DOSDP.data_vars, domain=None, range=Optional[str])

slots.data_list_vars = Slot(uri=DOSDP.data_list_vars, name="data_list_vars", curie=DOSDP.curie('data_list_vars'),
                   model_uri=DOSDP.data_list_vars, domain=None, range=Optional[str])

slots.internal_vars = Slot(uri=DOSDP.internal_vars, name="internal_vars", curie=DOSDP.curie('internal_vars'),
                   model_uri=DOSDP.internal_vars, domain=None, range=Optional[Union[str, List[str]]])

slots.substitutions = Slot(uri=DOSDP.substitutions, name="substitutions", curie=DOSDP.curie('substitutions'),
                   model_uri=DOSDP.substitutions, domain=None, range=Optional[Union[Union[dict, RegexSub], List[Union[dict, RegexSub]]]])

slots.logical_axioms = Slot(uri=DOSDP.logical_axioms, name="logical_axioms", curie=DOSDP.curie('logical_axioms'),
                   model_uri=DOSDP.logical_axioms, domain=None, range=Optional[Union[Union[dict, PrintfOwl], List[Union[dict, PrintfOwl]]]])

slots.equivalentTo = Slot(uri=DOSDP.equivalentTo, name="equivalentTo", curie=DOSDP.curie('equivalentTo'),
                   model_uri=DOSDP.equivalentTo, domain=None, range=Optional[Union[dict, PrintfOwlConvenience]])

slots.subClassOf = Slot(uri=DOSDP.subClassOf, name="subClassOf", curie=DOSDP.curie('subClassOf'),
                   model_uri=DOSDP.subClassOf, domain=None, range=Optional[Union[dict, PrintfOwlConvenience]])

slots.GCI = Slot(uri=DOSDP.GCI, name="GCI", curie=DOSDP.curie('GCI'),
                   model_uri=DOSDP.GCI, domain=None, range=Optional[Union[dict, PrintfOwlConvenience]])

slots.disjointWith = Slot(uri=DOSDP.disjointWith, name="disjointWith", curie=DOSDP.curie('disjointWith'),
                   model_uri=DOSDP.disjointWith, domain=None, range=Optional[Union[dict, PrintfOwlConvenience]])

slots.name = Slot(uri=DOSDP.name, name="name", curie=DOSDP.curie('name'),
                   model_uri=DOSDP.name, domain=None, range=Optional[Union[dict, PrintfAnnotationObo]])

slots.comment = Slot(uri=DOSDP.comment, name="comment", curie=DOSDP.curie('comment'),
                   model_uri=DOSDP.comment, domain=None, range=Optional[Union[dict, PrintfAnnotationObo]])

slots.definition = Slot(uri=DOSDP.definition, name="definition", curie=DOSDP.curie('definition'),
                   model_uri=DOSDP.definition, domain=None, range=Optional[Union[dict, PrintfAnnotationObo]])

slots.namespace = Slot(uri=DOSDP.namespace, name="namespace", curie=DOSDP.curie('namespace'),
                   model_uri=DOSDP.namespace, domain=None, range=Optional[Union[dict, PrintfAnnotationObo]])

slots.exact_synonym = Slot(uri=DOSDP.exact_synonym, name="exact_synonym", curie=DOSDP.curie('exact_synonym'),
                   model_uri=DOSDP.exact_synonym, domain=None, range=Optional[Union[dict, ListAnnotationObo]])

slots.narrow_synonym = Slot(uri=DOSDP.narrow_synonym, name="narrow_synonym", curie=DOSDP.curie('narrow_synonym'),
                   model_uri=DOSDP.narrow_synonym, domain=None, range=Optional[Union[dict, ListAnnotationObo]])

slots.related_synonym = Slot(uri=DOSDP.related_synonym, name="related_synonym", curie=DOSDP.curie('related_synonym'),
                   model_uri=DOSDP.related_synonym, domain=None, range=Optional[Union[dict, ListAnnotationObo]])

slots.broad_synonym = Slot(uri=DOSDP.broad_synonym, name="broad_synonym", curie=DOSDP.curie('broad_synonym'),
                   model_uri=DOSDP.broad_synonym, domain=None, range=Optional[Union[dict, ListAnnotationObo]])

slots.xref = Slot(uri=DOSDP.xref, name="xref", curie=DOSDP.curie('xref'),
                   model_uri=DOSDP.xref, domain=None, range=Optional[Union[dict, ListAnnotationObo]])

slots.generated_synonyms = Slot(uri=DOSDP.generated_synonyms, name="generated_synonyms", curie=DOSDP.curie('generated_synonyms'),
                   model_uri=DOSDP.generated_synonyms, domain=None, range=Optional[Union[Union[dict, PrintfAnnotationObo], List[Union[dict, PrintfAnnotationObo]]]])

slots.generated_narrow_synonyms = Slot(uri=DOSDP.generated_narrow_synonyms, name="generated_narrow_synonyms", curie=DOSDP.curie('generated_narrow_synonyms'),
                   model_uri=DOSDP.generated_narrow_synonyms, domain=None, range=Optional[Union[Union[dict, PrintfAnnotationObo], List[Union[dict, PrintfAnnotationObo]]]])

slots.generated_broad_synonyms = Slot(uri=DOSDP.generated_broad_synonyms, name="generated_broad_synonyms", curie=DOSDP.curie('generated_broad_synonyms'),
                   model_uri=DOSDP.generated_broad_synonyms, domain=None, range=Optional[Union[Union[dict, PrintfAnnotationObo], List[Union[dict, PrintfAnnotationObo]]]])

slots.generated_related_synonyms = Slot(uri=DOSDP.generated_related_synonyms, name="generated_related_synonyms", curie=DOSDP.curie('generated_related_synonyms'),
                   model_uri=DOSDP.generated_related_synonyms, domain=None, range=Optional[Union[Union[dict, PrintfAnnotationObo], List[Union[dict, PrintfAnnotationObo]]]])

slots.instance_graph = Slot(uri=DOSDP.instance_graph, name="instance_graph", curie=DOSDP.curie('instance_graph'),
                   model_uri=DOSDP.instance_graph, domain=None, range=Optional[str])

slots.varDeclaration__var = Slot(uri=DOSDP.var, name="varDeclaration__var", curie=DOSDP.curie('var'),
                   model_uri=DOSDP.varDeclaration__var, domain=None, range=URIRef)

slots.varDeclaration__range = Slot(uri=DOSDP.range, name="varDeclaration__range", curie=DOSDP.curie('range'),
                   model_uri=DOSDP.varDeclaration__range, domain=None, range=Optional[str])

slots.aliasDeclaration__alias = Slot(uri=DOSDP.alias, name="aliasDeclaration__alias", curie=DOSDP.curie('alias'),
                   model_uri=DOSDP.aliasDeclaration__alias, domain=None, range=URIRef)

slots.aliasDeclaration__curie = Slot(uri=DOSDP.curie, name="aliasDeclaration__curie", curie=DOSDP.curie('curie'),
                   model_uri=DOSDP.aliasDeclaration__curie, domain=None, range=Optional[str])

slots.Pattern_pattern_name = Slot(uri=DOSDP.pattern_name, name="Pattern_pattern_name", curie=DOSDP.curie('pattern_name'),
                   model_uri=DOSDP.Pattern_pattern_name, domain=Pattern, range=Optional[str])

slots.Pattern_pattern_iri = Slot(uri=DOSDP.pattern_iri, name="Pattern_pattern_iri", curie=DOSDP.curie('pattern_iri'),
                   model_uri=DOSDP.Pattern_pattern_iri, domain=Pattern, range=Optional[str])

slots.Pattern_base_IRI = Slot(uri=DOSDP.base_IRI, name="Pattern_base_IRI", curie=DOSDP.curie('base_IRI'),
                   model_uri=DOSDP.Pattern_base_IRI, domain=Pattern, range=Optional[str])

slots.Pattern_contributors = Slot(uri=DOSDP.contributors, name="Pattern_contributors", curie=DOSDP.curie('contributors'),
                   model_uri=DOSDP.Pattern_contributors, domain=Pattern, range=Optional[Union[str, List[str]]])

slots.Pattern_description = Slot(uri=DOSDP.description, name="Pattern_description", curie=DOSDP.curie('description'),
                   model_uri=DOSDP.Pattern_description, domain=Pattern, range=Optional[str])

slots.Pattern_examples = Slot(uri=DOSDP.examples, name="Pattern_examples", curie=DOSDP.curie('examples'),
                   model_uri=DOSDP.Pattern_examples, domain=Pattern, range=Optional[str])

slots.Pattern_status = Slot(uri=DOSDP.status, name="Pattern_status", curie=DOSDP.curie('status'),
                   model_uri=DOSDP.Pattern_status, domain=Pattern, range=Optional[Union[str, "StatusOptions"]])

slots.Pattern_tags = Slot(uri=DOSDP.tags, name="Pattern_tags", curie=DOSDP.curie('tags'),
                   model_uri=DOSDP.Pattern_tags, domain=Pattern, range=Optional[str])

slots.Pattern_readable_identifiers = Slot(uri=DOSDP.readable_identifiers, name="Pattern_readable_identifiers", curie=DOSDP.curie('readable_identifiers'),
                   model_uri=DOSDP.Pattern_readable_identifiers, domain=Pattern, range=Optional[Union[str, List[str]]])

slots.Pattern_classes = Slot(uri=DOSDP.classes, name="Pattern_classes", curie=DOSDP.curie('classes'),
                   model_uri=DOSDP.Pattern_classes, domain=Pattern, range=Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]])

slots.Pattern_objectProperties = Slot(uri=DOSDP.objectProperties, name="Pattern_objectProperties", curie=DOSDP.curie('objectProperties'),
                   model_uri=DOSDP.Pattern_objectProperties, domain=Pattern, range=Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]])

slots.Pattern_relations = Slot(uri=DOSDP.relations, name="Pattern_relations", curie=DOSDP.curie('relations'),
                   model_uri=DOSDP.Pattern_relations, domain=Pattern, range=Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]])

slots.Pattern_dataProperties = Slot(uri=DOSDP.dataProperties, name="Pattern_dataProperties", curie=DOSDP.curie('dataProperties'),
                   model_uri=DOSDP.Pattern_dataProperties, domain=Pattern, range=Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]])

slots.Pattern_annotationProperties = Slot(uri=DOSDP.annotationProperties, name="Pattern_annotationProperties", curie=DOSDP.curie('annotationProperties'),
                   model_uri=DOSDP.Pattern_annotationProperties, domain=Pattern, range=Optional[Union[Dict[Union[str, AliasDeclarationAlias], Union[dict, "AliasDeclaration"]], List[Union[dict, "AliasDeclaration"]]]])

slots.Pattern_vars = Slot(uri=DOSDP.vars, name="Pattern_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.Pattern_vars, domain=Pattern, range=Optional[Union[Dict[Union[str, VarDeclarationVar], Union[dict, "VarDeclaration"]], List[Union[dict, "VarDeclaration"]]]])

slots.Pattern_list_vars = Slot(uri=DOSDP.list_vars, name="Pattern_list_vars", curie=DOSDP.curie('list_vars'),
                   model_uri=DOSDP.Pattern_list_vars, domain=Pattern, range=Optional[str])

slots.Pattern_data_vars = Slot(uri=DOSDP.data_vars, name="Pattern_data_vars", curie=DOSDP.curie('data_vars'),
                   model_uri=DOSDP.Pattern_data_vars, domain=Pattern, range=Optional[str])

slots.Pattern_data_list_vars = Slot(uri=DOSDP.data_list_vars, name="Pattern_data_list_vars", curie=DOSDP.curie('data_list_vars'),
                   model_uri=DOSDP.Pattern_data_list_vars, domain=Pattern, range=Optional[str])

slots.Pattern_internal_vars = Slot(uri=DOSDP.internal_vars, name="Pattern_internal_vars", curie=DOSDP.curie('internal_vars'),
                   model_uri=DOSDP.Pattern_internal_vars, domain=Pattern, range=Optional[Union[str, List[str]]])

slots.Pattern_substitutions = Slot(uri=DOSDP.substitutions, name="Pattern_substitutions", curie=DOSDP.curie('substitutions'),
                   model_uri=DOSDP.Pattern_substitutions, domain=Pattern, range=Optional[Union[Union[dict, "RegexSub"], List[Union[dict, "RegexSub"]]]])

slots.Pattern_annotations = Slot(uri=DOSDP.annotations, name="Pattern_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.Pattern_annotations, domain=Pattern, range=Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]])

slots.Pattern_logical_axioms = Slot(uri=DOSDP.logical_axioms, name="Pattern_logical_axioms", curie=DOSDP.curie('logical_axioms'),
                   model_uri=DOSDP.Pattern_logical_axioms, domain=Pattern, range=Optional[Union[Union[dict, "PrintfOwl"], List[Union[dict, "PrintfOwl"]]]])

slots.Pattern_equivalentTo = Slot(uri=DOSDP.equivalentTo, name="Pattern_equivalentTo", curie=DOSDP.curie('equivalentTo'),
                   model_uri=DOSDP.Pattern_equivalentTo, domain=Pattern, range=Optional[Union[dict, "PrintfOwlConvenience"]])

slots.Pattern_subClassOf = Slot(uri=DOSDP.subClassOf, name="Pattern_subClassOf", curie=DOSDP.curie('subClassOf'),
                   model_uri=DOSDP.Pattern_subClassOf, domain=Pattern, range=Optional[Union[dict, "PrintfOwlConvenience"]])

slots.Pattern_GCI = Slot(uri=DOSDP.GCI, name="Pattern_GCI", curie=DOSDP.curie('GCI'),
                   model_uri=DOSDP.Pattern_GCI, domain=Pattern, range=Optional[Union[dict, "PrintfOwlConvenience"]])

slots.Pattern_disjointWith = Slot(uri=DOSDP.disjointWith, name="Pattern_disjointWith", curie=DOSDP.curie('disjointWith'),
                   model_uri=DOSDP.Pattern_disjointWith, domain=Pattern, range=Optional[Union[dict, "PrintfOwlConvenience"]])

slots.Pattern_name = Slot(uri=DOSDP.name, name="Pattern_name", curie=DOSDP.curie('name'),
                   model_uri=DOSDP.Pattern_name, domain=Pattern, range=Optional[Union[dict, "PrintfAnnotationObo"]])

slots.Pattern_comment = Slot(uri=DOSDP.comment, name="Pattern_comment", curie=DOSDP.curie('comment'),
                   model_uri=DOSDP.Pattern_comment, domain=Pattern, range=Optional[Union[dict, "PrintfAnnotationObo"]])

slots.Pattern_definition = Slot(uri=DOSDP.definition, name="Pattern_definition", curie=DOSDP.curie('definition'),
                   model_uri=DOSDP.Pattern_definition, domain=Pattern, range=Optional[Union[dict, "PrintfAnnotationObo"]])

slots.Pattern_namespace = Slot(uri=DOSDP.namespace, name="Pattern_namespace", curie=DOSDP.curie('namespace'),
                   model_uri=DOSDP.Pattern_namespace, domain=Pattern, range=Optional[Union[dict, "PrintfAnnotationObo"]])

slots.Pattern_exact_synonym = Slot(uri=DOSDP.exact_synonym, name="Pattern_exact_synonym", curie=DOSDP.curie('exact_synonym'),
                   model_uri=DOSDP.Pattern_exact_synonym, domain=Pattern, range=Optional[Union[dict, "ListAnnotationObo"]])

slots.Pattern_narrow_synonym = Slot(uri=DOSDP.narrow_synonym, name="Pattern_narrow_synonym", curie=DOSDP.curie('narrow_synonym'),
                   model_uri=DOSDP.Pattern_narrow_synonym, domain=Pattern, range=Optional[Union[dict, "ListAnnotationObo"]])

slots.Pattern_related_synonym = Slot(uri=DOSDP.related_synonym, name="Pattern_related_synonym", curie=DOSDP.curie('related_synonym'),
                   model_uri=DOSDP.Pattern_related_synonym, domain=Pattern, range=Optional[Union[dict, "ListAnnotationObo"]])

slots.Pattern_broad_synonym = Slot(uri=DOSDP.broad_synonym, name="Pattern_broad_synonym", curie=DOSDP.curie('broad_synonym'),
                   model_uri=DOSDP.Pattern_broad_synonym, domain=Pattern, range=Optional[Union[dict, "ListAnnotationObo"]])

slots.Pattern_xref = Slot(uri=DOSDP.xref, name="Pattern_xref", curie=DOSDP.curie('xref'),
                   model_uri=DOSDP.Pattern_xref, domain=Pattern, range=Optional[Union[dict, "ListAnnotationObo"]])

slots.Pattern_generated_synonyms = Slot(uri=DOSDP.generated_synonyms, name="Pattern_generated_synonyms", curie=DOSDP.curie('generated_synonyms'),
                   model_uri=DOSDP.Pattern_generated_synonyms, domain=Pattern, range=Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]])

slots.Pattern_generated_narrow_synonyms = Slot(uri=DOSDP.generated_narrow_synonyms, name="Pattern_generated_narrow_synonyms", curie=DOSDP.curie('generated_narrow_synonyms'),
                   model_uri=DOSDP.Pattern_generated_narrow_synonyms, domain=Pattern, range=Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]])

slots.Pattern_generated_broad_synonyms = Slot(uri=DOSDP.generated_broad_synonyms, name="Pattern_generated_broad_synonyms", curie=DOSDP.curie('generated_broad_synonyms'),
                   model_uri=DOSDP.Pattern_generated_broad_synonyms, domain=Pattern, range=Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]])

slots.Pattern_generated_related_synonyms = Slot(uri=DOSDP.generated_related_synonyms, name="Pattern_generated_related_synonyms", curie=DOSDP.curie('generated_related_synonyms'),
                   model_uri=DOSDP.Pattern_generated_related_synonyms, domain=Pattern, range=Optional[Union[Union[dict, "PrintfAnnotationObo"], List[Union[dict, "PrintfAnnotationObo"]]]])

slots.Pattern_instance_graph = Slot(uri=DOSDP.instance_graph, name="Pattern_instance_graph", curie=DOSDP.curie('instance_graph'),
                   model_uri=DOSDP.Pattern_instance_graph, domain=Pattern, range=Optional[str])

slots.MultiClausePrintf_sep = Slot(uri=DOSDP.sep, name="MultiClausePrintf_sep", curie=DOSDP.curie('sep'),
                   model_uri=DOSDP.MultiClausePrintf_sep, domain=MultiClausePrintf, range=Optional[str])

slots.MultiClausePrintf_clauses = Slot(uri=DOSDP.clauses, name="MultiClausePrintf_clauses", curie=DOSDP.curie('clauses'),
                   model_uri=DOSDP.MultiClausePrintf_clauses, domain=MultiClausePrintf, range=Union[Union[dict, "PrintfClause"], List[Union[dict, "PrintfClause"]]])

slots.PrintfClause_text = Slot(uri=DOSDP.text, name="PrintfClause_text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.PrintfClause_text, domain=PrintfClause, range=str)

slots.PrintfClause_vars = Slot(uri=DOSDP.vars, name="PrintfClause_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.PrintfClause_vars, domain=PrintfClause, range=Union[str, List[str]])

slots.PrintfClause_sub_clauses = Slot(uri=DOSDP.sub_clauses, name="PrintfClause_sub_clauses", curie=DOSDP.curie('sub_clauses'),
                   model_uri=DOSDP.PrintfClause_sub_clauses, domain=PrintfClause, range=Optional[Union[Union[dict, MultiClausePrintf], List[Union[dict, MultiClausePrintf]]]])

slots.Join_sep = Slot(uri=DOSDP.sep, name="Join_sep", curie=DOSDP.curie('sep'),
                   model_uri=DOSDP.Join_sep, domain=Join, range=Optional[str])

slots.PrintfAnnotation_annotationProperty = Slot(uri=DOSDP.annotationProperty, name="PrintfAnnotation_annotationProperty", curie=DOSDP.curie('annotationProperty'),
                   model_uri=DOSDP.PrintfAnnotation_annotationProperty, domain=PrintfAnnotation, range=str)

slots.PrintfAnnotation_annotations = Slot(uri=DOSDP.annotations, name="PrintfAnnotation_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.PrintfAnnotation_annotations, domain=PrintfAnnotation, range=Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]])

slots.PrintfAnnotation_text = Slot(uri=DOSDP.text, name="PrintfAnnotation_text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.PrintfAnnotation_text, domain=PrintfAnnotation, range=Optional[str])

slots.PrintfAnnotation_vars = Slot(uri=DOSDP.vars, name="PrintfAnnotation_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.PrintfAnnotation_vars, domain=PrintfAnnotation, range=Optional[Union[str, List[str]]])

slots.PrintfAnnotation_multi_clause = Slot(uri=DOSDP.multi_clause, name="PrintfAnnotation_multi_clause", curie=DOSDP.curie('multi_clause'),
                   model_uri=DOSDP.PrintfAnnotation_multi_clause, domain=PrintfAnnotation, range=Optional[str])

slots.ListAnnotation_annotationProperty = Slot(uri=DOSDP.annotationProperty, name="ListAnnotation_annotationProperty", curie=DOSDP.curie('annotationProperty'),
                   model_uri=DOSDP.ListAnnotation_annotationProperty, domain=ListAnnotation, range=str)

slots.ListAnnotation_value = Slot(uri=DOSDP.value, name="ListAnnotation_value", curie=DOSDP.curie('value'),
                   model_uri=DOSDP.ListAnnotation_value, domain=ListAnnotation, range=str)

slots.IriValueAnnotation_annotationProperty = Slot(uri=DOSDP.annotationProperty, name="IriValueAnnotation_annotationProperty", curie=DOSDP.curie('annotationProperty'),
                   model_uri=DOSDP.IriValueAnnotation_annotationProperty, domain=IriValueAnnotation, range=str)

slots.IriValueAnnotation_var = Slot(uri=DOSDP.var, name="IriValueAnnotation_var", curie=DOSDP.curie('var'),
                   model_uri=DOSDP.IriValueAnnotation_var, domain=IriValueAnnotation, range=str)

slots.IriValueAnnotation_annotations = Slot(uri=DOSDP.annotations, name="IriValueAnnotation_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.IriValueAnnotation_annotations, domain=IriValueAnnotation, range=Optional[Union[Union[dict, "Annotation"], List[Union[dict, "Annotation"]]]])

slots.PrintfOwl_annotations = Slot(uri=DOSDP.annotations, name="PrintfOwl_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.PrintfOwl_annotations, domain=PrintfOwl, range=Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]])

slots.PrintfOwl_axiom_type = Slot(uri=DOSDP.axiom_type, name="PrintfOwl_axiom_type", curie=DOSDP.curie('axiom_type'),
                   model_uri=DOSDP.PrintfOwl_axiom_type, domain=PrintfOwl, range=Optional[Union[str, "AxiomTypeOptions"]])

slots.PrintfOwl_text = Slot(uri=DOSDP.text, name="PrintfOwl_text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.PrintfOwl_text, domain=PrintfOwl, range=Optional[str])

slots.PrintfOwl_vars = Slot(uri=DOSDP.vars, name="PrintfOwl_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.PrintfOwl_vars, domain=PrintfOwl, range=Optional[Union[str, List[str]]])

slots.PrintfOwl_multi_clause = Slot(uri=DOSDP.multi_clause, name="PrintfOwl_multi_clause", curie=DOSDP.curie('multi_clause'),
                   model_uri=DOSDP.PrintfOwl_multi_clause, domain=PrintfOwl, range=Optional[str])

slots.PrintfOwlConvenience_annotations = Slot(uri=DOSDP.annotations, name="PrintfOwlConvenience_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.PrintfOwlConvenience_annotations, domain=PrintfOwlConvenience, range=Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]])

slots.PrintfOwlConvenience_text = Slot(uri=DOSDP.text, name="PrintfOwlConvenience_text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.PrintfOwlConvenience_text, domain=PrintfOwlConvenience, range=Optional[str])

slots.PrintfOwlConvenience_vars = Slot(uri=DOSDP.vars, name="PrintfOwlConvenience_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.PrintfOwlConvenience_vars, domain=PrintfOwlConvenience, range=Optional[Union[str, List[str]]])

slots.PrintfOwlConvenience_multi_clause = Slot(uri=DOSDP.multi_clause, name="PrintfOwlConvenience_multi_clause", curie=DOSDP.curie('multi_clause'),
                   model_uri=DOSDP.PrintfOwlConvenience_multi_clause, domain=PrintfOwlConvenience, range=Optional[str])

slots.RegexSub__in = Slot(uri=DOSDP._in, name="RegexSub__in", curie=DOSDP.curie('_in'),
                   model_uri=DOSDP.RegexSub__in, domain=RegexSub, range=Optional[str])

slots.RegexSub_out = Slot(uri=DOSDP.out, name="RegexSub_out", curie=DOSDP.curie('out'),
                   model_uri=DOSDP.RegexSub_out, domain=RegexSub, range=str)

slots.RegexSub_match = Slot(uri=DOSDP.match, name="RegexSub_match", curie=DOSDP.curie('match'),
                   model_uri=DOSDP.RegexSub_match, domain=RegexSub, range=str)

slots.RegexSub_sub = Slot(uri=DOSDP.sub, name="RegexSub_sub", curie=DOSDP.curie('sub'),
                   model_uri=DOSDP.RegexSub_sub, domain=RegexSub, range=str)

slots.OPA_edge = Slot(uri=DOSDP.edge, name="OPA_edge", curie=DOSDP.curie('edge'),
                   model_uri=DOSDP.OPA_edge, domain=OPA, range=Union[str, List[str]])

slots.OPA_annotations = Slot(uri=DOSDP.annotations, name="OPA_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.OPA_annotations, domain=OPA, range=Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]])

slots.OPA__not = Slot(uri=DOSDP._not, name="OPA__not", curie=DOSDP.curie('_not'),
                   model_uri=DOSDP.OPA__not, domain=OPA, range=Optional[Union[bool, Bool]])

slots.PrintfAnnotationObo_annotations = Slot(uri=DOSDP.annotations, name="PrintfAnnotationObo_annotations", curie=DOSDP.curie('annotations'),
                   model_uri=DOSDP.PrintfAnnotationObo_annotations, domain=PrintfAnnotationObo, range=Optional[Union[Union[dict, Annotation], List[Union[dict, Annotation]]]])

slots.PrintfAnnotationObo_xrefs = Slot(uri=DOSDP.xrefs, name="PrintfAnnotationObo_xrefs", curie=DOSDP.curie('xrefs'),
                   model_uri=DOSDP.PrintfAnnotationObo_xrefs, domain=PrintfAnnotationObo, range=Optional[str])

slots.PrintfAnnotationObo_text = Slot(uri=DOSDP.text, name="PrintfAnnotationObo_text", curie=DOSDP.curie('text'),
                   model_uri=DOSDP.PrintfAnnotationObo_text, domain=PrintfAnnotationObo, range=Optional[str])

slots.PrintfAnnotationObo_vars = Slot(uri=DOSDP.vars, name="PrintfAnnotationObo_vars", curie=DOSDP.curie('vars'),
                   model_uri=DOSDP.PrintfAnnotationObo_vars, domain=PrintfAnnotationObo, range=Optional[Union[str, List[str]]])

slots.PrintfAnnotationObo_multi_clause = Slot(uri=DOSDP.multi_clause, name="PrintfAnnotationObo_multi_clause", curie=DOSDP.curie('multi_clause'),
                   model_uri=DOSDP.PrintfAnnotationObo_multi_clause, domain=PrintfAnnotationObo, range=Optional[str])

slots.ListAnnotationObo_value = Slot(uri=DOSDP.value, name="ListAnnotationObo_value", curie=DOSDP.curie('value'),
                   model_uri=DOSDP.ListAnnotationObo_value, domain=ListAnnotationObo, range=str)

slots.ListAnnotationObo_xrefs = Slot(uri=DOSDP.xrefs, name="ListAnnotationObo_xrefs", curie=DOSDP.curie('xrefs'),
                   model_uri=DOSDP.ListAnnotationObo_xrefs, domain=ListAnnotationObo, range=Optional[str])
