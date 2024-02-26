# Auto generated from cadsr.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-02-24T19:17:52
# Schema: cadsr
#
# id: https://example.org/cadsr
# description:
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
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
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
CADSR = CurieNamespace('cadsr', 'https://example.org/cadsr')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = CADSR


# Types

# Class references



@dataclass
class DataElementContainer(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementContainer"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementContainer"
    class_name: ClassVar[str] = "DataElementContainer"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementContainer

    DataElement: Optional[Union[dict, "DataElement"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.DataElement is not None and not isinstance(self.DataElement, DataElement):
            self.DataElement = DataElement(**as_dict(self.DataElement))

        super().__post_init__(**kwargs)


@dataclass
class ClassificationScheme(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ClassificationScheme"]
    class_class_curie: ClassVar[str] = "cadsr:ClassificationScheme"
    class_name: ClassVar[str] = "ClassificationScheme"
    class_model_uri: ClassVar[URIRef] = CADSR.ClassificationScheme

    publicId: Optional[str] = None
    version: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    ClassificationSchemeItems: Optional[Union[Union[dict, "ClassificationSchemeItem"], List[Union[dict, "ClassificationSchemeItem"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if not isinstance(self.ClassificationSchemeItems, list):
            self.ClassificationSchemeItems = [self.ClassificationSchemeItems] if self.ClassificationSchemeItems is not None else []
        self.ClassificationSchemeItems = [v if isinstance(v, ClassificationSchemeItem) else ClassificationSchemeItem(**as_dict(v)) for v in self.ClassificationSchemeItems]

        super().__post_init__(**kwargs)


@dataclass
class Property(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["Property"]
    class_class_curie: ClassVar[str] = "cadsr:Property"
    class_name: ClassVar[str] = "Property"
    class_model_uri: ClassVar[URIRef] = CADSR.Property

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    Concepts: Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]] = empty_list()
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if not isinstance(self.Concepts, list):
            self.Concepts = [self.Concepts] if self.Concepts is not None else []
        self.Concepts = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.Concepts]

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class DataElementpublicIdGETResponse(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementpublicIdGETResponse"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementpublicIdGETResponse"
    class_name: ClassVar[str] = "DataElementpublicId_GET_response"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementpublicIdGETResponse

    DataElement: Optional[Union[dict, "DataElement"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.DataElement is not None and not isinstance(self.DataElement, DataElement):
            self.DataElement = DataElement(**as_dict(self.DataElement))

        super().__post_init__(**kwargs)


@dataclass
class DataElementgetCRDCListGETResponse(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementgetCRDCListGETResponse"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementgetCRDCListGETResponse"
    class_name: ClassVar[str] = "DataElementgetCRDCList_GET_response"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementgetCRDCListGETResponse

    CRDCDataElements: Optional[Union[Union[dict, "CRDCDataElement"], List[Union[dict, "CRDCDataElement"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.CRDCDataElements, list):
            self.CRDCDataElements = [self.CRDCDataElements] if self.CRDCDataElements is not None else []
        self.CRDCDataElements = [v if isinstance(v, CRDCDataElement) else CRDCDataElement(**as_dict(v)) for v in self.CRDCDataElements]

        super().__post_init__(**kwargs)


@dataclass
class DataElementqueryContextGETResponse(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementqueryContextGETResponse"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementqueryContextGETResponse"
    class_name: ClassVar[str] = "DataElementqueryContext_GET_response"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementqueryContextGETResponse

    numRecords: Optional[str] = None
    DataElementQueryResults: Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.numRecords is not None and not isinstance(self.numRecords, str):
            self.numRecords = str(self.numRecords)

        if not isinstance(self.DataElementQueryResults, list):
            self.DataElementQueryResults = [self.DataElementQueryResults] if self.DataElementQueryResults is not None else []
        self.DataElementQueryResults = [v if isinstance(v, DataElementQuery) else DataElementQuery(**as_dict(v)) for v in self.DataElementQueryResults]

        super().__post_init__(**kwargs)


@dataclass
class AlternateName(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["AlternateName"]
    class_class_curie: ClassVar[str] = "cadsr:AlternateName"
    class_name: ClassVar[str] = "AlternateName"
    class_model_uri: ClassVar[URIRef] = CADSR.AlternateName

    name: Optional[str] = None
    type: Optional[str] = None
    context: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.type is not None and not isinstance(self.type, str):
            self.type = str(self.type)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        super().__post_init__(**kwargs)


@dataclass
class CRDCDataElement(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["CRDCDataElement"]
    class_class_curie: ClassVar[str] = "cadsr:CRDCDataElement"
    class_name: ClassVar[str] = "CRDCDataElement"
    class_model_uri: ClassVar[URIRef] = CADSR.CRDCDataElement

    CDE_Public_ID: Optional[str] = None
    Version: Optional[str] = None
    CRDC_Name: Optional[str] = None
    CRD_Domain: Optional[str] = None
    Example: Optional[str] = None
    VD_Type: Optional[str] = None
    Coding_Instruction: Optional[str] = None
    Instructions: Optional[str] = None
    CRDC_Definition: Optional[str] = None
    CDE_Long_Name: Optional[str] = None
    Registration_Status: Optional[str] = None
    Workflow_Status: Optional[str] = None
    Owned_By: Optional[str] = None
    Used_By: Optional[str] = None
    Deep_Link: Optional[str] = None
    permissibleValues: Optional[Union[Union[dict, "PermissibleValue"], List[Union[dict, "PermissibleValue"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.CDE_Public_ID is not None and not isinstance(self.CDE_Public_ID, str):
            self.CDE_Public_ID = str(self.CDE_Public_ID)

        if self.Version is not None and not isinstance(self.Version, str):
            self.Version = str(self.Version)

        if self.CRDC_Name is not None and not isinstance(self.CRDC_Name, str):
            self.CRDC_Name = str(self.CRDC_Name)

        if self.CRD_Domain is not None and not isinstance(self.CRD_Domain, str):
            self.CRD_Domain = str(self.CRD_Domain)

        if self.Example is not None and not isinstance(self.Example, str):
            self.Example = str(self.Example)

        if self.VD_Type is not None and not isinstance(self.VD_Type, str):
            self.VD_Type = str(self.VD_Type)

        if self.Coding_Instruction is not None and not isinstance(self.Coding_Instruction, str):
            self.Coding_Instruction = str(self.Coding_Instruction)

        if self.Instructions is not None and not isinstance(self.Instructions, str):
            self.Instructions = str(self.Instructions)

        if self.CRDC_Definition is not None and not isinstance(self.CRDC_Definition, str):
            self.CRDC_Definition = str(self.CRDC_Definition)

        if self.CDE_Long_Name is not None and not isinstance(self.CDE_Long_Name, str):
            self.CDE_Long_Name = str(self.CDE_Long_Name)

        if self.Registration_Status is not None and not isinstance(self.Registration_Status, str):
            self.Registration_Status = str(self.Registration_Status)

        if self.Workflow_Status is not None and not isinstance(self.Workflow_Status, str):
            self.Workflow_Status = str(self.Workflow_Status)

        if self.Owned_By is not None and not isinstance(self.Owned_By, str):
            self.Owned_By = str(self.Owned_By)

        if self.Used_By is not None and not isinstance(self.Used_By, str):
            self.Used_By = str(self.Used_By)

        if self.Deep_Link is not None and not isinstance(self.Deep_Link, str):
            self.Deep_Link = str(self.Deep_Link)

        if not isinstance(self.permissibleValues, list):
            self.permissibleValues = [self.permissibleValues] if self.permissibleValues is not None else []
        self.permissibleValues = [v if isinstance(v, PermissibleValue) else PermissibleValue(**as_dict(v)) for v in self.permissibleValues]

        super().__post_init__(**kwargs)


@dataclass
class ConceptualDomain(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ConceptualDomain"]
    class_class_curie: ClassVar[str] = "cadsr:ConceptualDomain"
    class_name: ClassVar[str] = "ConceptualDomain"
    class_model_uri: ClassVar[URIRef] = CADSR.ConceptualDomain

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class ClassificationSchemeItem(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ClassificationSchemeItem"]
    class_class_curie: ClassVar[str] = "cadsr:ClassificationSchemeItem"
    class_name: ClassVar[str] = "ClassificationSchemeItem"
    class_model_uri: ClassVar[URIRef] = CADSR.ClassificationSchemeItem

    publicId: Optional[str] = None
    version: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        super().__post_init__(**kwargs)


@dataclass
class DataElementqueryConceptGETResponse(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementqueryConceptGETResponse"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementqueryConceptGETResponse"
    class_name: ClassVar[str] = "DataElementqueryConcept_GET_response"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementqueryConceptGETResponse

    numRecords: Optional[str] = None
    DataElementQueryResults: Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.numRecords is not None and not isinstance(self.numRecords, str):
            self.numRecords = str(self.numRecords)

        if not isinstance(self.DataElementQueryResults, list):
            self.DataElementQueryResults = [self.DataElementQueryResults] if self.DataElementQueryResults is not None else []
        self.DataElementQueryResults = [v if isinstance(v, DataElementQuery) else DataElementQuery(**as_dict(v)) for v in self.DataElementQueryResults]

        super().__post_init__(**kwargs)


@dataclass
class DataElement(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElement"]
    class_class_curie: ClassVar[str] = "cadsr:DataElement"
    class_name: ClassVar[str] = "DataElement"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElement

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    DataElementConcept: Optional[Union[dict, "DataElementConcept"]] = None
    ValueDomain: Optional[Union[dict, "ValueDomain"]] = None
    ClassificationSchemes: Optional[Union[Union[dict, ClassificationScheme], List[Union[dict, ClassificationScheme]]]] = empty_list()
    AlternateNames: Optional[Union[Union[dict, AlternateName], List[Union[dict, AlternateName]]]] = empty_list()
    ReferenceDocuments: Optional[Union[Union[dict, "ReferenceDocument"], List[Union[dict, "ReferenceDocument"]]]] = empty_list()
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if self.DataElementConcept is not None and not isinstance(self.DataElementConcept, DataElementConcept):
            self.DataElementConcept = DataElementConcept(**as_dict(self.DataElementConcept))

        if self.ValueDomain is not None and not isinstance(self.ValueDomain, ValueDomain):
            self.ValueDomain = ValueDomain(**as_dict(self.ValueDomain))

        if not isinstance(self.ClassificationSchemes, list):
            self.ClassificationSchemes = [self.ClassificationSchemes] if self.ClassificationSchemes is not None else []
        self.ClassificationSchemes = [v if isinstance(v, ClassificationScheme) else ClassificationScheme(**as_dict(v)) for v in self.ClassificationSchemes]

        if not isinstance(self.AlternateNames, list):
            self.AlternateNames = [self.AlternateNames] if self.AlternateNames is not None else []
        self.AlternateNames = [v if isinstance(v, AlternateName) else AlternateName(**as_dict(v)) for v in self.AlternateNames]

        if not isinstance(self.ReferenceDocuments, list):
            self.ReferenceDocuments = [self.ReferenceDocuments] if self.ReferenceDocuments is not None else []
        self.ReferenceDocuments = [v if isinstance(v, ReferenceDocument) else ReferenceDocument(**as_dict(v)) for v in self.ReferenceDocuments]

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class ValueDomain(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ValueDomain"]
    class_class_curie: ClassVar[str] = "cadsr:ValueDomain"
    class_name: ClassVar[str] = "ValueDomain"
    class_model_uri: ClassVar[URIRef] = CADSR.ValueDomain

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    type: Optional[str] = None
    dataType: Optional[str] = None
    unitOfMeasure: Optional[str] = None
    characterSet: Optional[str] = None
    minLength: Optional[str] = None
    maxLength: Optional[str] = None
    minValue: Optional[str] = None
    maxValue: Optional[str] = None
    decimalPlace: Optional[str] = None
    format: Optional[str] = None
    PermissibleValues: Optional[Union[Union[dict, "CDEPermissibleValue"], List[Union[dict, "CDEPermissibleValue"]]]] = empty_list()
    ConceptualDomain: Optional[Union[dict, ConceptualDomain]] = None
    RepresentationTerm: Optional[Union[dict, "RepresentationTerm"]] = None
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if self.type is not None and not isinstance(self.type, str):
            self.type = str(self.type)

        if self.dataType is not None and not isinstance(self.dataType, str):
            self.dataType = str(self.dataType)

        if self.unitOfMeasure is not None and not isinstance(self.unitOfMeasure, str):
            self.unitOfMeasure = str(self.unitOfMeasure)

        if self.characterSet is not None and not isinstance(self.characterSet, str):
            self.characterSet = str(self.characterSet)

        if self.minLength is not None and not isinstance(self.minLength, str):
            self.minLength = str(self.minLength)

        if self.maxLength is not None and not isinstance(self.maxLength, str):
            self.maxLength = str(self.maxLength)

        if self.minValue is not None and not isinstance(self.minValue, str):
            self.minValue = str(self.minValue)

        if self.maxValue is not None and not isinstance(self.maxValue, str):
            self.maxValue = str(self.maxValue)

        if self.decimalPlace is not None and not isinstance(self.decimalPlace, str):
            self.decimalPlace = str(self.decimalPlace)

        if self.format is not None and not isinstance(self.format, str):
            self.format = str(self.format)

        if not isinstance(self.PermissibleValues, list):
            self.PermissibleValues = [self.PermissibleValues] if self.PermissibleValues is not None else []
        self.PermissibleValues = [v if isinstance(v, CDEPermissibleValue) else CDEPermissibleValue(**as_dict(v)) for v in self.PermissibleValues]

        if self.ConceptualDomain is not None and not isinstance(self.ConceptualDomain, ConceptualDomain):
            self.ConceptualDomain = ConceptualDomain(**as_dict(self.ConceptualDomain))

        if self.RepresentationTerm is not None and not isinstance(self.RepresentationTerm, RepresentationTerm):
            self.RepresentationTerm = RepresentationTerm(**as_dict(self.RepresentationTerm))

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class ObjectClass(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ObjectClass"]
    class_class_curie: ClassVar[str] = "cadsr:ObjectClass"
    class_name: ClassVar[str] = "ObjectClass"
    class_model_uri: ClassVar[URIRef] = CADSR.ObjectClass

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    Concepts: Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]] = empty_list()
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if not isinstance(self.Concepts, list):
            self.Concepts = [self.Concepts] if self.Concepts is not None else []
        self.Concepts = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.Concepts]

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class DataElementqueryGETResponse(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementqueryGETResponse"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementqueryGETResponse"
    class_name: ClassVar[str] = "DataElementquery_GET_response"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementqueryGETResponse

    numRecords: Optional[str] = None
    DataElementQueryResults: Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.numRecords is not None and not isinstance(self.numRecords, str):
            self.numRecords = str(self.numRecords)

        if not isinstance(self.DataElementQueryResults, list):
            self.DataElementQueryResults = [self.DataElementQueryResults] if self.DataElementQueryResults is not None else []
        self.DataElementQueryResults = [v if isinstance(v, DataElementQuery) else DataElementQuery(**as_dict(v)) for v in self.DataElementQueryResults]

        super().__post_init__(**kwargs)


@dataclass
class Concept(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["Concept"]
    class_class_curie: ClassVar[str] = "cadsr:Concept"
    class_name: ClassVar[str] = "Concept"
    class_model_uri: ClassVar[URIRef] = CADSR.Concept

    longName: Optional[str] = None
    conceptCode: Optional[str] = None
    definition: Optional[str] = None
    evsSource: Optional[str] = None
    primaryIndicator: Optional[str] = None
    displayOrder: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.conceptCode is not None and not isinstance(self.conceptCode, str):
            self.conceptCode = str(self.conceptCode)

        if self.definition is not None and not isinstance(self.definition, str):
            self.definition = str(self.definition)

        if self.evsSource is not None and not isinstance(self.evsSource, str):
            self.evsSource = str(self.evsSource)

        if self.primaryIndicator is not None and not isinstance(self.primaryIndicator, str):
            self.primaryIndicator = str(self.primaryIndicator)

        if self.displayOrder is not None and not isinstance(self.displayOrder, str):
            self.displayOrder = str(self.displayOrder)

        super().__post_init__(**kwargs)


@dataclass
class DataElementConcept(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementConcept"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementConcept"
    class_name: ClassVar[str] = "DataElementConcept"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementConcept

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    ObjectClass: Optional[Union[dict, ObjectClass]] = None
    Property: Optional[Union[dict, Property]] = None
    ConceptualDomain: Optional[Union[dict, ConceptualDomain]] = None
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if self.ObjectClass is not None and not isinstance(self.ObjectClass, ObjectClass):
            self.ObjectClass = ObjectClass(**as_dict(self.ObjectClass))

        if self.Property is not None and not isinstance(self.Property, Property):
            self.Property = Property(**as_dict(self.Property))

        if self.ConceptualDomain is not None and not isinstance(self.ConceptualDomain, ConceptualDomain):
            self.ConceptualDomain = ConceptualDomain(**as_dict(self.ConceptualDomain))

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class ValueMeaning(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ValueMeaning"]
    class_class_curie: ClassVar[str] = "cadsr:ValueMeaning"
    class_name: ClassVar[str] = "ValueMeaning"
    class_model_uri: ClassVar[URIRef] = CADSR.ValueMeaning

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    longName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    Concepts: Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]] = empty_list()
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if not isinstance(self.Concepts, list):
            self.Concepts = [self.Concepts] if self.Concepts is not None else []
        self.Concepts = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.Concepts]

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class RepresentationTerm(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["RepresentationTerm"]
    class_class_curie: ClassVar[str] = "cadsr:RepresentationTerm"
    class_name: ClassVar[str] = "RepresentationTerm"
    class_model_uri: ClassVar[URIRef] = CADSR.RepresentationTerm

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    context: Optional[str] = None
    contextVersion: Optional[str] = None
    Concepts: Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]] = empty_list()
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeDescription: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if not isinstance(self.Concepts, list):
            self.Concepts = [self.Concepts] if self.Concepts is not None else []
        self.Concepts = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.Concepts]

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeDescription is not None and not isinstance(self.changeDescription, str):
            self.changeDescription = str(self.changeDescription)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class ReferenceDocument(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["ReferenceDocument"]
    class_class_curie: ClassVar[str] = "cadsr:ReferenceDocument"
    class_name: ClassVar[str] = "ReferenceDocument"
    class_model_uri: ClassVar[URIRef] = CADSR.ReferenceDocument

    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    context: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.type is not None and not isinstance(self.type, str):
            self.type = str(self.type)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.url is not None and not isinstance(self.url, str):
            self.url = str(self.url)

        if self.context is not None and not isinstance(self.context, str):
            self.context = str(self.context)

        super().__post_init__(**kwargs)


@dataclass
class CDEPermissibleValue(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["CDEPermissibleValue"]
    class_class_curie: ClassVar[str] = "cadsr:CDEPermissibleValue"
    class_name: ClassVar[str] = "CDEPermissibleValue"
    class_model_uri: ClassVar[URIRef] = CADSR.CDEPermissibleValue

    publicId: Optional[str] = None
    value: Optional[str] = None
    valueDescription: Optional[str] = None
    ValueMeaning: Optional[Union[dict, ValueMeaning]] = None
    origin: Optional[str] = None
    id: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.value is not None and not isinstance(self.value, str):
            self.value = str(self.value)

        if self.valueDescription is not None and not isinstance(self.valueDescription, str):
            self.valueDescription = str(self.valueDescription)

        if self.ValueMeaning is not None and not isinstance(self.ValueMeaning, ValueMeaning):
            self.ValueMeaning = ValueMeaning(**as_dict(self.ValueMeaning))

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class DataElementQuery(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["DataElementQuery"]
    class_class_curie: ClassVar[str] = "cadsr:DataElementQuery"
    class_name: ClassVar[str] = "DataElementQuery"
    class_model_uri: ClassVar[URIRef] = CADSR.DataElementQuery

    publicId: Optional[str] = None
    version: Optional[str] = None
    preferredName: Optional[str] = None
    preferredDefinition: Optional[str] = None
    longName: Optional[str] = None
    contextName: Optional[str] = None
    contextVersion: Optional[str] = None
    dataElementConceptPublicId: Optional[str] = None
    dataElementConceptVersion: Optional[str] = None
    valueDomainPublicId: Optional[str] = None
    valueDomainVersion: Optional[str] = None
    origin: Optional[str] = None
    workflowStatus: Optional[str] = None
    registrationStatus: Optional[str] = None
    id: Optional[str] = None
    latestVersionIndicator: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    dateCreated: Optional[str] = None
    modifiedBy: Optional[str] = None
    dateModified: Optional[str] = None
    changeNote: Optional[str] = None
    administrativeNotes: Optional[str] = None
    unresolvedIssues: Optional[str] = None
    deletedIndicator: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.publicId is not None and not isinstance(self.publicId, str):
            self.publicId = str(self.publicId)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.preferredName is not None and not isinstance(self.preferredName, str):
            self.preferredName = str(self.preferredName)

        if self.preferredDefinition is not None and not isinstance(self.preferredDefinition, str):
            self.preferredDefinition = str(self.preferredDefinition)

        if self.longName is not None and not isinstance(self.longName, str):
            self.longName = str(self.longName)

        if self.contextName is not None and not isinstance(self.contextName, str):
            self.contextName = str(self.contextName)

        if self.contextVersion is not None and not isinstance(self.contextVersion, str):
            self.contextVersion = str(self.contextVersion)

        if self.dataElementConceptPublicId is not None and not isinstance(self.dataElementConceptPublicId, str):
            self.dataElementConceptPublicId = str(self.dataElementConceptPublicId)

        if self.dataElementConceptVersion is not None and not isinstance(self.dataElementConceptVersion, str):
            self.dataElementConceptVersion = str(self.dataElementConceptVersion)

        if self.valueDomainPublicId is not None and not isinstance(self.valueDomainPublicId, str):
            self.valueDomainPublicId = str(self.valueDomainPublicId)

        if self.valueDomainVersion is not None and not isinstance(self.valueDomainVersion, str):
            self.valueDomainVersion = str(self.valueDomainVersion)

        if self.origin is not None and not isinstance(self.origin, str):
            self.origin = str(self.origin)

        if self.workflowStatus is not None and not isinstance(self.workflowStatus, str):
            self.workflowStatus = str(self.workflowStatus)

        if self.registrationStatus is not None and not isinstance(self.registrationStatus, str):
            self.registrationStatus = str(self.registrationStatus)

        if self.id is not None and not isinstance(self.id, str):
            self.id = str(self.id)

        if self.latestVersionIndicator is not None and not isinstance(self.latestVersionIndicator, str):
            self.latestVersionIndicator = str(self.latestVersionIndicator)

        if self.beginDate is not None and not isinstance(self.beginDate, str):
            self.beginDate = str(self.beginDate)

        if self.endDate is not None and not isinstance(self.endDate, str):
            self.endDate = str(self.endDate)

        if self.createdBy is not None and not isinstance(self.createdBy, str):
            self.createdBy = str(self.createdBy)

        if self.dateCreated is not None and not isinstance(self.dateCreated, str):
            self.dateCreated = str(self.dateCreated)

        if self.modifiedBy is not None and not isinstance(self.modifiedBy, str):
            self.modifiedBy = str(self.modifiedBy)

        if self.dateModified is not None and not isinstance(self.dateModified, str):
            self.dateModified = str(self.dateModified)

        if self.changeNote is not None and not isinstance(self.changeNote, str):
            self.changeNote = str(self.changeNote)

        if self.administrativeNotes is not None and not isinstance(self.administrativeNotes, str):
            self.administrativeNotes = str(self.administrativeNotes)

        if self.unresolvedIssues is not None and not isinstance(self.unresolvedIssues, str):
            self.unresolvedIssues = str(self.unresolvedIssues)

        if self.deletedIndicator is not None and not isinstance(self.deletedIndicator, str):
            self.deletedIndicator = str(self.deletedIndicator)

        super().__post_init__(**kwargs)


@dataclass
class PermissibleValue(YAMLRoot):
    """
    List of Permissible Values
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CADSR["PermissibleValue"]
    class_class_curie: ClassVar[str] = "cadsr:PermissibleValue"
    class_name: ClassVar[str] = "permissibleValue"
    class_model_uri: ClassVar[URIRef] = CADSR.PermissibleValue

    Permissible_Value: Optional[str] = None
    VM_Long_Name: Optional[str] = None
    VM_Public_ID: Optional[str] = None
    Concept_Code: Optional[str] = None
    VM_Description: Optional[str] = None
    Begin_Date: Optional[str] = None
    End_Date: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.Permissible_Value is not None and not isinstance(self.Permissible_Value, str):
            self.Permissible_Value = str(self.Permissible_Value)

        if self.VM_Long_Name is not None and not isinstance(self.VM_Long_Name, str):
            self.VM_Long_Name = str(self.VM_Long_Name)

        if self.VM_Public_ID is not None and not isinstance(self.VM_Public_ID, str):
            self.VM_Public_ID = str(self.VM_Public_ID)

        if self.Concept_Code is not None and not isinstance(self.Concept_Code, str):
            self.Concept_Code = str(self.Concept_Code)

        if self.VM_Description is not None and not isinstance(self.VM_Description, str):
            self.VM_Description = str(self.VM_Description)

        if self.Begin_Date is not None and not isinstance(self.Begin_Date, str):
            self.Begin_Date = str(self.Begin_Date)

        if self.End_Date is not None and not isinstance(self.End_Date, str):
            self.End_Date = str(self.End_Date)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.publicId = Slot(uri=CADSR.publicId, name="publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.publicId, domain=None, range=Optional[str])

slots.version = Slot(uri=CADSR.version, name="version", curie=CADSR.curie('version'),
                   model_uri=CADSR.version, domain=None, range=Optional[str])

slots.longName = Slot(uri=CADSR.longName, name="longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.longName, domain=None, range=Optional[str])

slots.context = Slot(uri=CADSR.context, name="context", curie=CADSR.curie('context'),
                   model_uri=CADSR.context, domain=None, range=Optional[str])

slots.ClassificationSchemeItems = Slot(uri=CADSR.ClassificationSchemeItems, name="ClassificationSchemeItems", curie=CADSR.curie('ClassificationSchemeItems'),
                   model_uri=CADSR.ClassificationSchemeItems, domain=None, range=Optional[Union[Union[dict, ClassificationSchemeItem], List[Union[dict, ClassificationSchemeItem]]]])

slots.preferredName = Slot(uri=CADSR.preferredName, name="preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.preferredName, domain=None, range=Optional[str])

slots.preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.preferredDefinition, domain=None, range=Optional[str])

slots.contextVersion = Slot(uri=CADSR.contextVersion, name="contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.contextVersion, domain=None, range=Optional[str])

slots.Concepts = Slot(uri=CADSR.Concepts, name="Concepts", curie=CADSR.curie('Concepts'),
                   model_uri=CADSR.Concepts, domain=None, range=Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]])

slots.origin = Slot(uri=CADSR.origin, name="origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.origin, domain=None, range=Optional[str])

slots.workflowStatus = Slot(uri=CADSR.workflowStatus, name="workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.workflowStatus, domain=None, range=Optional[str])

slots.registrationStatus = Slot(uri=CADSR.registrationStatus, name="registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.registrationStatus, domain=None, range=Optional[str])

slots.id = Slot(uri=CADSR.id, name="id", curie=CADSR.curie('id'),
                   model_uri=CADSR.id, domain=None, range=Optional[str])

slots.latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.latestVersionIndicator, domain=None, range=Optional[str])

slots.beginDate = Slot(uri=CADSR.beginDate, name="beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.beginDate, domain=None, range=Optional[str])

slots.endDate = Slot(uri=CADSR.endDate, name="endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.endDate, domain=None, range=Optional[str])

slots.createdBy = Slot(uri=CADSR.createdBy, name="createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.createdBy, domain=None, range=Optional[str])

slots.dateCreated = Slot(uri=CADSR.dateCreated, name="dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.dateCreated, domain=None, range=Optional[str])

slots.modifiedBy = Slot(uri=CADSR.modifiedBy, name="modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.modifiedBy, domain=None, range=Optional[str])

slots.dateModified = Slot(uri=CADSR.dateModified, name="dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.dateModified, domain=None, range=Optional[str])

slots.changeDescription = Slot(uri=CADSR.changeDescription, name="changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.changeDescription, domain=None, range=Optional[str])

slots.administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.administrativeNotes, domain=None, range=Optional[str])

slots.unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.unresolvedIssues, domain=None, range=Optional[str])

slots.deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.deletedIndicator, domain=None, range=Optional[str])

slots.DataElement = Slot(uri=CADSR.DataElement, name="DataElement", curie=CADSR.curie('DataElement'),
                   model_uri=CADSR.DataElement, domain=None, range=Optional[Union[dict, DataElement]])

slots.CRDCDataElements = Slot(uri=CADSR.CRDCDataElements, name="CRDCDataElements", curie=CADSR.curie('CRDCDataElements'),
                   model_uri=CADSR.CRDCDataElements, domain=None, range=Optional[Union[Union[dict, CRDCDataElement], List[Union[dict, CRDCDataElement]]]])

slots.numRecords = Slot(uri=CADSR.numRecords, name="numRecords", curie=CADSR.curie('numRecords'),
                   model_uri=CADSR.numRecords, domain=None, range=Optional[str])

slots.DataElementQueryResults = Slot(uri=CADSR.DataElementQueryResults, name="DataElementQueryResults", curie=CADSR.curie('DataElementQueryResults'),
                   model_uri=CADSR.DataElementQueryResults, domain=None, range=Optional[Union[Union[dict, DataElementQuery], List[Union[dict, DataElementQuery]]]])

slots.name = Slot(uri=CADSR.name, name="name", curie=CADSR.curie('name'),
                   model_uri=CADSR.name, domain=None, range=Optional[str])

slots.type = Slot(uri=CADSR.type, name="type", curie=CADSR.curie('type'),
                   model_uri=CADSR.type, domain=None, range=Optional[str])

slots.CDE_Public_ID = Slot(uri=CADSR.CDE_Public_ID, name="CDE Public ID", curie=CADSR.curie('CDE_Public_ID'),
                   model_uri=CADSR.CDE_Public_ID, domain=None, range=Optional[str])

slots.Version = Slot(uri=CADSR.Version, name="Version", curie=CADSR.curie('Version'),
                   model_uri=CADSR.Version, domain=None, range=Optional[str])

slots.CRDC_Name = Slot(uri=CADSR.CRDC_Name, name="CRDC Name", curie=CADSR.curie('CRDC_Name'),
                   model_uri=CADSR.CRDC_Name, domain=None, range=Optional[str])

slots.CRD_Domain = Slot(uri=CADSR.CRD_Domain, name="CRD Domain", curie=CADSR.curie('CRD_Domain'),
                   model_uri=CADSR.CRD_Domain, domain=None, range=Optional[str])

slots.Example = Slot(uri=CADSR.Example, name="Example", curie=CADSR.curie('Example'),
                   model_uri=CADSR.Example, domain=None, range=Optional[str])

slots.VD_Type = Slot(uri=CADSR.VD_Type, name="VD Type", curie=CADSR.curie('VD_Type'),
                   model_uri=CADSR.VD_Type, domain=None, range=Optional[str])

slots.Coding_Instruction = Slot(uri=CADSR.Coding_Instruction, name="Coding Instruction", curie=CADSR.curie('Coding_Instruction'),
                   model_uri=CADSR.Coding_Instruction, domain=None, range=Optional[str])

slots.Instructions = Slot(uri=CADSR.Instructions, name="Instructions", curie=CADSR.curie('Instructions'),
                   model_uri=CADSR.Instructions, domain=None, range=Optional[str])

slots.CRDC_Definition = Slot(uri=CADSR.CRDC_Definition, name="CRDC Definition", curie=CADSR.curie('CRDC_Definition'),
                   model_uri=CADSR.CRDC_Definition, domain=None, range=Optional[str])

slots.CDE_Long_Name = Slot(uri=CADSR.CDE_Long_Name, name="CDE Long Name", curie=CADSR.curie('CDE_Long_Name'),
                   model_uri=CADSR.CDE_Long_Name, domain=None, range=Optional[str])

slots.Registration_Status = Slot(uri=CADSR.Registration_Status, name="Registration Status", curie=CADSR.curie('Registration_Status'),
                   model_uri=CADSR.Registration_Status, domain=None, range=Optional[str])

slots.Workflow_Status = Slot(uri=CADSR.Workflow_Status, name="Workflow Status", curie=CADSR.curie('Workflow_Status'),
                   model_uri=CADSR.Workflow_Status, domain=None, range=Optional[str])

slots.Owned_By = Slot(uri=CADSR.Owned_By, name="Owned By", curie=CADSR.curie('Owned_By'),
                   model_uri=CADSR.Owned_By, domain=None, range=Optional[str])

slots.Used_By = Slot(uri=CADSR.Used_By, name="Used By", curie=CADSR.curie('Used_By'),
                   model_uri=CADSR.Used_By, domain=None, range=Optional[str])

slots.Deep_Link = Slot(uri=CADSR.Deep_Link, name="Deep Link", curie=CADSR.curie('Deep_Link'),
                   model_uri=CADSR.Deep_Link, domain=None, range=Optional[str])

slots.permissibleValues = Slot(uri=CADSR.permissibleValues, name="permissibleValues", curie=CADSR.curie('permissibleValues'),
                   model_uri=CADSR.permissibleValues, domain=None, range=Optional[Union[Union[dict, PermissibleValue], List[Union[dict, PermissibleValue]]]])

slots.DataElementConcept = Slot(uri=CADSR.DataElementConcept, name="DataElementConcept", curie=CADSR.curie('DataElementConcept'),
                   model_uri=CADSR.DataElementConcept, domain=None, range=Optional[Union[dict, DataElementConcept]])

slots.ValueDomain = Slot(uri=CADSR.ValueDomain, name="ValueDomain", curie=CADSR.curie('ValueDomain'),
                   model_uri=CADSR.ValueDomain, domain=None, range=Optional[Union[dict, ValueDomain]])

slots.ClassificationSchemes = Slot(uri=CADSR.ClassificationSchemes, name="ClassificationSchemes", curie=CADSR.curie('ClassificationSchemes'),
                   model_uri=CADSR.ClassificationSchemes, domain=None, range=Optional[Union[Union[dict, ClassificationScheme], List[Union[dict, ClassificationScheme]]]])

slots.AlternateNames = Slot(uri=CADSR.AlternateNames, name="AlternateNames", curie=CADSR.curie('AlternateNames'),
                   model_uri=CADSR.AlternateNames, domain=None, range=Optional[Union[Union[dict, AlternateName], List[Union[dict, AlternateName]]]])

slots.ReferenceDocuments = Slot(uri=CADSR.ReferenceDocuments, name="ReferenceDocuments", curie=CADSR.curie('ReferenceDocuments'),
                   model_uri=CADSR.ReferenceDocuments, domain=None, range=Optional[Union[Union[dict, ReferenceDocument], List[Union[dict, ReferenceDocument]]]])

slots.dataType = Slot(uri=CADSR.dataType, name="dataType", curie=CADSR.curie('dataType'),
                   model_uri=CADSR.dataType, domain=None, range=Optional[str])

slots.unitOfMeasure = Slot(uri=CADSR.unitOfMeasure, name="unitOfMeasure", curie=CADSR.curie('unitOfMeasure'),
                   model_uri=CADSR.unitOfMeasure, domain=None, range=Optional[str])

slots.characterSet = Slot(uri=CADSR.characterSet, name="characterSet", curie=CADSR.curie('characterSet'),
                   model_uri=CADSR.characterSet, domain=None, range=Optional[str])

slots.minLength = Slot(uri=CADSR.minLength, name="minLength", curie=CADSR.curie('minLength'),
                   model_uri=CADSR.minLength, domain=None, range=Optional[str])

slots.maxLength = Slot(uri=CADSR.maxLength, name="maxLength", curie=CADSR.curie('maxLength'),
                   model_uri=CADSR.maxLength, domain=None, range=Optional[str])

slots.minValue = Slot(uri=CADSR.minValue, name="minValue", curie=CADSR.curie('minValue'),
                   model_uri=CADSR.minValue, domain=None, range=Optional[str])

slots.maxValue = Slot(uri=CADSR.maxValue, name="maxValue", curie=CADSR.curie('maxValue'),
                   model_uri=CADSR.maxValue, domain=None, range=Optional[str])

slots.decimalPlace = Slot(uri=CADSR.decimalPlace, name="decimalPlace", curie=CADSR.curie('decimalPlace'),
                   model_uri=CADSR.decimalPlace, domain=None, range=Optional[str])

slots.format = Slot(uri=CADSR.format, name="format", curie=CADSR.curie('format'),
                   model_uri=CADSR.format, domain=None, range=Optional[str])

slots.PermissibleValues = Slot(uri=CADSR.PermissibleValues, name="PermissibleValues", curie=CADSR.curie('PermissibleValues'),
                   model_uri=CADSR.PermissibleValues, domain=None, range=Optional[Union[Union[dict, CDEPermissibleValue], List[Union[dict, CDEPermissibleValue]]]])

slots.ConceptualDomain = Slot(uri=CADSR.ConceptualDomain, name="ConceptualDomain", curie=CADSR.curie('ConceptualDomain'),
                   model_uri=CADSR.ConceptualDomain, domain=None, range=Optional[Union[dict, ConceptualDomain]])

slots.RepresentationTerm = Slot(uri=CADSR.RepresentationTerm, name="RepresentationTerm", curie=CADSR.curie('RepresentationTerm'),
                   model_uri=CADSR.RepresentationTerm, domain=None, range=Optional[Union[dict, RepresentationTerm]])

slots.conceptCode = Slot(uri=CADSR.conceptCode, name="conceptCode", curie=CADSR.curie('conceptCode'),
                   model_uri=CADSR.conceptCode, domain=None, range=Optional[str])

slots.definition = Slot(uri=CADSR.definition, name="definition", curie=CADSR.curie('definition'),
                   model_uri=CADSR.definition, domain=None, range=Optional[str])

slots.evsSource = Slot(uri=CADSR.evsSource, name="evsSource", curie=CADSR.curie('evsSource'),
                   model_uri=CADSR.evsSource, domain=None, range=Optional[str])

slots.primaryIndicator = Slot(uri=CADSR.primaryIndicator, name="primaryIndicator", curie=CADSR.curie('primaryIndicator'),
                   model_uri=CADSR.primaryIndicator, domain=None, range=Optional[str])

slots.displayOrder = Slot(uri=CADSR.displayOrder, name="displayOrder", curie=CADSR.curie('displayOrder'),
                   model_uri=CADSR.displayOrder, domain=None, range=Optional[str])

slots.ObjectClass = Slot(uri=CADSR.ObjectClass, name="ObjectClass", curie=CADSR.curie('ObjectClass'),
                   model_uri=CADSR.ObjectClass, domain=None, range=Optional[Union[dict, ObjectClass]])

slots.Property = Slot(uri=CADSR.Property, name="Property", curie=CADSR.curie('Property'),
                   model_uri=CADSR.Property, domain=None, range=Optional[Union[dict, Property]])

slots.description = Slot(uri=CADSR.description, name="description", curie=CADSR.curie('description'),
                   model_uri=CADSR.description, domain=None, range=Optional[str])

slots.url = Slot(uri=CADSR.url, name="url", curie=CADSR.curie('url'),
                   model_uri=CADSR.url, domain=None, range=Optional[str])

slots.value = Slot(uri=CADSR.value, name="value", curie=CADSR.curie('value'),
                   model_uri=CADSR.value, domain=None, range=Optional[str])

slots.valueDescription = Slot(uri=CADSR.valueDescription, name="valueDescription", curie=CADSR.curie('valueDescription'),
                   model_uri=CADSR.valueDescription, domain=None, range=Optional[str])

slots.ValueMeaning = Slot(uri=CADSR.ValueMeaning, name="ValueMeaning", curie=CADSR.curie('ValueMeaning'),
                   model_uri=CADSR.ValueMeaning, domain=None, range=Optional[Union[dict, ValueMeaning]])

slots.contextName = Slot(uri=CADSR.contextName, name="contextName", curie=CADSR.curie('contextName'),
                   model_uri=CADSR.contextName, domain=None, range=Optional[str])

slots.dataElementConceptPublicId = Slot(uri=CADSR.dataElementConceptPublicId, name="dataElementConceptPublicId", curie=CADSR.curie('dataElementConceptPublicId'),
                   model_uri=CADSR.dataElementConceptPublicId, domain=None, range=Optional[str])

slots.dataElementConceptVersion = Slot(uri=CADSR.dataElementConceptVersion, name="dataElementConceptVersion", curie=CADSR.curie('dataElementConceptVersion'),
                   model_uri=CADSR.dataElementConceptVersion, domain=None, range=Optional[str])

slots.valueDomainPublicId = Slot(uri=CADSR.valueDomainPublicId, name="valueDomainPublicId", curie=CADSR.curie('valueDomainPublicId'),
                   model_uri=CADSR.valueDomainPublicId, domain=None, range=Optional[str])

slots.valueDomainVersion = Slot(uri=CADSR.valueDomainVersion, name="valueDomainVersion", curie=CADSR.curie('valueDomainVersion'),
                   model_uri=CADSR.valueDomainVersion, domain=None, range=Optional[str])

slots.changeNote = Slot(uri=CADSR.changeNote, name="changeNote", curie=CADSR.curie('changeNote'),
                   model_uri=CADSR.changeNote, domain=None, range=Optional[str])

slots.Permissible_Value = Slot(uri=CADSR.Permissible_Value, name="Permissible Value", curie=CADSR.curie('Permissible_Value'),
                   model_uri=CADSR.Permissible_Value, domain=None, range=Optional[str])

slots.VM_Long_Name = Slot(uri=CADSR.VM_Long_Name, name="VM Long Name", curie=CADSR.curie('VM_Long_Name'),
                   model_uri=CADSR.VM_Long_Name, domain=None, range=Optional[str])

slots.VM_Public_ID = Slot(uri=CADSR.VM_Public_ID, name="VM Public ID", curie=CADSR.curie('VM_Public_ID'),
                   model_uri=CADSR.VM_Public_ID, domain=None, range=Optional[str])

slots.Concept_Code = Slot(uri=CADSR.Concept_Code, name="Concept Code", curie=CADSR.curie('Concept_Code'),
                   model_uri=CADSR.Concept_Code, domain=None, range=Optional[str])

slots.VM_Description = Slot(uri=CADSR.VM_Description, name="VM Description", curie=CADSR.curie('VM_Description'),
                   model_uri=CADSR.VM_Description, domain=None, range=Optional[str])

slots.Begin_Date = Slot(uri=CADSR.Begin_Date, name="Begin Date", curie=CADSR.curie('Begin_Date'),
                   model_uri=CADSR.Begin_Date, domain=None, range=Optional[str])

slots.End_Date = Slot(uri=CADSR.End_Date, name="End Date", curie=CADSR.curie('End_Date'),
                   model_uri=CADSR.End_Date, domain=None, range=Optional[str])

slots.ClassificationScheme_publicId = Slot(uri=CADSR.publicId, name="ClassificationScheme_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ClassificationScheme_publicId, domain=ClassificationScheme, range=Optional[str])

slots.ClassificationScheme_version = Slot(uri=CADSR.version, name="ClassificationScheme_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ClassificationScheme_version, domain=ClassificationScheme, range=Optional[str])

slots.ClassificationScheme_longName = Slot(uri=CADSR.longName, name="ClassificationScheme_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ClassificationScheme_longName, domain=ClassificationScheme, range=Optional[str])

slots.ClassificationScheme_context = Slot(uri=CADSR.context, name="ClassificationScheme_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ClassificationScheme_context, domain=ClassificationScheme, range=Optional[str])

slots.ClassificationScheme_ClassificationSchemeItems = Slot(uri=CADSR.ClassificationSchemeItems, name="ClassificationScheme_ClassificationSchemeItems", curie=CADSR.curie('ClassificationSchemeItems'),
                   model_uri=CADSR.ClassificationScheme_ClassificationSchemeItems, domain=ClassificationScheme, range=Optional[Union[Union[dict, "ClassificationSchemeItem"], List[Union[dict, "ClassificationSchemeItem"]]]])

slots.Property_publicId = Slot(uri=CADSR.publicId, name="Property_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.Property_publicId, domain=Property, range=Optional[str])

slots.Property_version = Slot(uri=CADSR.version, name="Property_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.Property_version, domain=Property, range=Optional[str])

slots.Property_preferredName = Slot(uri=CADSR.preferredName, name="Property_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.Property_preferredName, domain=Property, range=Optional[str])

slots.Property_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="Property_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.Property_preferredDefinition, domain=Property, range=Optional[str])

slots.Property_longName = Slot(uri=CADSR.longName, name="Property_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.Property_longName, domain=Property, range=Optional[str])

slots.Property_context = Slot(uri=CADSR.context, name="Property_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.Property_context, domain=Property, range=Optional[str])

slots.Property_contextVersion = Slot(uri=CADSR.contextVersion, name="Property_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.Property_contextVersion, domain=Property, range=Optional[str])

slots.Property_Concepts = Slot(uri=CADSR.Concepts, name="Property_Concepts", curie=CADSR.curie('Concepts'),
                   model_uri=CADSR.Property_Concepts, domain=Property, range=Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]])

slots.Property_origin = Slot(uri=CADSR.origin, name="Property_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.Property_origin, domain=Property, range=Optional[str])

slots.Property_workflowStatus = Slot(uri=CADSR.workflowStatus, name="Property_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.Property_workflowStatus, domain=Property, range=Optional[str])

slots.Property_registrationStatus = Slot(uri=CADSR.registrationStatus, name="Property_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.Property_registrationStatus, domain=Property, range=Optional[str])

slots.Property_id = Slot(uri=CADSR.id, name="Property_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.Property_id, domain=Property, range=Optional[str])

slots.Property_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="Property_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.Property_latestVersionIndicator, domain=Property, range=Optional[str])

slots.Property_beginDate = Slot(uri=CADSR.beginDate, name="Property_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.Property_beginDate, domain=Property, range=Optional[str])

slots.Property_endDate = Slot(uri=CADSR.endDate, name="Property_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.Property_endDate, domain=Property, range=Optional[str])

slots.Property_createdBy = Slot(uri=CADSR.createdBy, name="Property_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.Property_createdBy, domain=Property, range=Optional[str])

slots.Property_dateCreated = Slot(uri=CADSR.dateCreated, name="Property_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.Property_dateCreated, domain=Property, range=Optional[str])

slots.Property_modifiedBy = Slot(uri=CADSR.modifiedBy, name="Property_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.Property_modifiedBy, domain=Property, range=Optional[str])

slots.Property_dateModified = Slot(uri=CADSR.dateModified, name="Property_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.Property_dateModified, domain=Property, range=Optional[str])

slots.Property_changeDescription = Slot(uri=CADSR.changeDescription, name="Property_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.Property_changeDescription, domain=Property, range=Optional[str])

slots.Property_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="Property_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.Property_administrativeNotes, domain=Property, range=Optional[str])

slots.Property_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="Property_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.Property_unresolvedIssues, domain=Property, range=Optional[str])

slots.Property_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="Property_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.Property_deletedIndicator, domain=Property, range=Optional[str])

slots.DataElementpublicId_GET_response_DataElement = Slot(uri=CADSR.DataElement, name="DataElementpublicId_GET_response_DataElement", curie=CADSR.curie('DataElement'),
                   model_uri=CADSR.DataElementpublicId_GET_response_DataElement, domain=DataElementpublicIdGETResponse, range=Optional[Union[dict, "DataElement"]])

slots.DataElementgetCRDCList_GET_response_CRDCDataElements = Slot(uri=CADSR.CRDCDataElements, name="DataElementgetCRDCList_GET_response_CRDCDataElements", curie=CADSR.curie('CRDCDataElements'),
                   model_uri=CADSR.DataElementgetCRDCList_GET_response_CRDCDataElements, domain=DataElementgetCRDCListGETResponse, range=Optional[Union[Union[dict, "CRDCDataElement"], List[Union[dict, "CRDCDataElement"]]]])

slots.DataElementqueryContext_GET_response_numRecords = Slot(uri=CADSR.numRecords, name="DataElementqueryContext_GET_response_numRecords", curie=CADSR.curie('numRecords'),
                   model_uri=CADSR.DataElementqueryContext_GET_response_numRecords, domain=DataElementqueryContextGETResponse, range=Optional[str])

slots.DataElementqueryContext_GET_response_DataElementQueryResults = Slot(uri=CADSR.DataElementQueryResults, name="DataElementqueryContext_GET_response_DataElementQueryResults", curie=CADSR.curie('DataElementQueryResults'),
                   model_uri=CADSR.DataElementqueryContext_GET_response_DataElementQueryResults, domain=DataElementqueryContextGETResponse, range=Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]])

slots.AlternateName_type = Slot(uri=CADSR.type, name="AlternateName_type", curie=CADSR.curie('type'),
                   model_uri=CADSR.AlternateName_type, domain=AlternateName, range=Optional[str])

slots.AlternateName_context = Slot(uri=CADSR.context, name="AlternateName_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.AlternateName_context, domain=AlternateName, range=Optional[str])

slots.CRDCDataElement_CDE_Public_ID = Slot(uri=CADSR.CDE_Public_ID, name="CRDCDataElement_CDE Public ID", curie=CADSR.curie('CDE_Public_ID'),
                   model_uri=CADSR.CRDCDataElement_CDE_Public_ID, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Version = Slot(uri=CADSR.Version, name="CRDCDataElement_Version", curie=CADSR.curie('Version'),
                   model_uri=CADSR.CRDCDataElement_Version, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_CRDC_Name = Slot(uri=CADSR.CRDC_Name, name="CRDCDataElement_CRDC Name", curie=CADSR.curie('CRDC_Name'),
                   model_uri=CADSR.CRDCDataElement_CRDC_Name, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_CRD_Domain = Slot(uri=CADSR.CRD_Domain, name="CRDCDataElement_CRD Domain", curie=CADSR.curie('CRD_Domain'),
                   model_uri=CADSR.CRDCDataElement_CRD_Domain, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Example = Slot(uri=CADSR.Example, name="CRDCDataElement_Example", curie=CADSR.curie('Example'),
                   model_uri=CADSR.CRDCDataElement_Example, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_VD_Type = Slot(uri=CADSR.VD_Type, name="CRDCDataElement_VD Type", curie=CADSR.curie('VD_Type'),
                   model_uri=CADSR.CRDCDataElement_VD_Type, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Coding_Instruction = Slot(uri=CADSR.Coding_Instruction, name="CRDCDataElement_Coding Instruction", curie=CADSR.curie('Coding_Instruction'),
                   model_uri=CADSR.CRDCDataElement_Coding_Instruction, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Instructions = Slot(uri=CADSR.Instructions, name="CRDCDataElement_Instructions", curie=CADSR.curie('Instructions'),
                   model_uri=CADSR.CRDCDataElement_Instructions, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_CRDC_Definition = Slot(uri=CADSR.CRDC_Definition, name="CRDCDataElement_CRDC Definition", curie=CADSR.curie('CRDC_Definition'),
                   model_uri=CADSR.CRDCDataElement_CRDC_Definition, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_CDE_Long_Name = Slot(uri=CADSR.CDE_Long_Name, name="CRDCDataElement_CDE Long Name", curie=CADSR.curie('CDE_Long_Name'),
                   model_uri=CADSR.CRDCDataElement_CDE_Long_Name, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Registration_Status = Slot(uri=CADSR.Registration_Status, name="CRDCDataElement_Registration Status", curie=CADSR.curie('Registration_Status'),
                   model_uri=CADSR.CRDCDataElement_Registration_Status, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Workflow_Status = Slot(uri=CADSR.Workflow_Status, name="CRDCDataElement_Workflow Status", curie=CADSR.curie('Workflow_Status'),
                   model_uri=CADSR.CRDCDataElement_Workflow_Status, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Owned_By = Slot(uri=CADSR.Owned_By, name="CRDCDataElement_Owned By", curie=CADSR.curie('Owned_By'),
                   model_uri=CADSR.CRDCDataElement_Owned_By, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Used_By = Slot(uri=CADSR.Used_By, name="CRDCDataElement_Used By", curie=CADSR.curie('Used_By'),
                   model_uri=CADSR.CRDCDataElement_Used_By, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_Deep_Link = Slot(uri=CADSR.Deep_Link, name="CRDCDataElement_Deep Link", curie=CADSR.curie('Deep_Link'),
                   model_uri=CADSR.CRDCDataElement_Deep_Link, domain=CRDCDataElement, range=Optional[str])

slots.CRDCDataElement_permissibleValues = Slot(uri=CADSR.permissibleValues, name="CRDCDataElement_permissibleValues", curie=CADSR.curie('permissibleValues'),
                   model_uri=CADSR.CRDCDataElement_permissibleValues, domain=CRDCDataElement, range=Optional[Union[Union[dict, "PermissibleValue"], List[Union[dict, "PermissibleValue"]]]])

slots.ConceptualDomain_publicId = Slot(uri=CADSR.publicId, name="ConceptualDomain_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ConceptualDomain_publicId, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_version = Slot(uri=CADSR.version, name="ConceptualDomain_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ConceptualDomain_version, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_preferredName = Slot(uri=CADSR.preferredName, name="ConceptualDomain_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.ConceptualDomain_preferredName, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="ConceptualDomain_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.ConceptualDomain_preferredDefinition, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_longName = Slot(uri=CADSR.longName, name="ConceptualDomain_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ConceptualDomain_longName, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_context = Slot(uri=CADSR.context, name="ConceptualDomain_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ConceptualDomain_context, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_contextVersion = Slot(uri=CADSR.contextVersion, name="ConceptualDomain_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.ConceptualDomain_contextVersion, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_origin = Slot(uri=CADSR.origin, name="ConceptualDomain_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.ConceptualDomain_origin, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_workflowStatus = Slot(uri=CADSR.workflowStatus, name="ConceptualDomain_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.ConceptualDomain_workflowStatus, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_registrationStatus = Slot(uri=CADSR.registrationStatus, name="ConceptualDomain_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.ConceptualDomain_registrationStatus, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_id = Slot(uri=CADSR.id, name="ConceptualDomain_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.ConceptualDomain_id, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="ConceptualDomain_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.ConceptualDomain_latestVersionIndicator, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_beginDate = Slot(uri=CADSR.beginDate, name="ConceptualDomain_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.ConceptualDomain_beginDate, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_endDate = Slot(uri=CADSR.endDate, name="ConceptualDomain_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.ConceptualDomain_endDate, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_createdBy = Slot(uri=CADSR.createdBy, name="ConceptualDomain_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.ConceptualDomain_createdBy, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_dateCreated = Slot(uri=CADSR.dateCreated, name="ConceptualDomain_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.ConceptualDomain_dateCreated, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_modifiedBy = Slot(uri=CADSR.modifiedBy, name="ConceptualDomain_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.ConceptualDomain_modifiedBy, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_dateModified = Slot(uri=CADSR.dateModified, name="ConceptualDomain_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.ConceptualDomain_dateModified, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_changeDescription = Slot(uri=CADSR.changeDescription, name="ConceptualDomain_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.ConceptualDomain_changeDescription, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="ConceptualDomain_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.ConceptualDomain_administrativeNotes, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="ConceptualDomain_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.ConceptualDomain_unresolvedIssues, domain=ConceptualDomain, range=Optional[str])

slots.ConceptualDomain_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="ConceptualDomain_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.ConceptualDomain_deletedIndicator, domain=ConceptualDomain, range=Optional[str])

slots.ClassificationSchemeItem_publicId = Slot(uri=CADSR.publicId, name="ClassificationSchemeItem_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ClassificationSchemeItem_publicId, domain=ClassificationSchemeItem, range=Optional[str])

slots.ClassificationSchemeItem_version = Slot(uri=CADSR.version, name="ClassificationSchemeItem_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ClassificationSchemeItem_version, domain=ClassificationSchemeItem, range=Optional[str])

slots.ClassificationSchemeItem_longName = Slot(uri=CADSR.longName, name="ClassificationSchemeItem_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ClassificationSchemeItem_longName, domain=ClassificationSchemeItem, range=Optional[str])

slots.ClassificationSchemeItem_context = Slot(uri=CADSR.context, name="ClassificationSchemeItem_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ClassificationSchemeItem_context, domain=ClassificationSchemeItem, range=Optional[str])

slots.DataElementqueryConcept_GET_response_numRecords = Slot(uri=CADSR.numRecords, name="DataElementqueryConcept_GET_response_numRecords", curie=CADSR.curie('numRecords'),
                   model_uri=CADSR.DataElementqueryConcept_GET_response_numRecords, domain=DataElementqueryConceptGETResponse, range=Optional[str])

slots.DataElementqueryConcept_GET_response_DataElementQueryResults = Slot(uri=CADSR.DataElementQueryResults, name="DataElementqueryConcept_GET_response_DataElementQueryResults", curie=CADSR.curie('DataElementQueryResults'),
                   model_uri=CADSR.DataElementqueryConcept_GET_response_DataElementQueryResults, domain=DataElementqueryConceptGETResponse, range=Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]])

slots.DataElement_publicId = Slot(uri=CADSR.publicId, name="DataElement_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.DataElement_publicId, domain=DataElement, range=Optional[str])

slots.DataElement_version = Slot(uri=CADSR.version, name="DataElement_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.DataElement_version, domain=DataElement, range=Optional[str])

slots.DataElement_preferredName = Slot(uri=CADSR.preferredName, name="DataElement_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.DataElement_preferredName, domain=DataElement, range=Optional[str])

slots.DataElement_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="DataElement_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.DataElement_preferredDefinition, domain=DataElement, range=Optional[str])

slots.DataElement_longName = Slot(uri=CADSR.longName, name="DataElement_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.DataElement_longName, domain=DataElement, range=Optional[str])

slots.DataElement_context = Slot(uri=CADSR.context, name="DataElement_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.DataElement_context, domain=DataElement, range=Optional[str])

slots.DataElement_contextVersion = Slot(uri=CADSR.contextVersion, name="DataElement_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.DataElement_contextVersion, domain=DataElement, range=Optional[str])

slots.DataElement_DataElementConcept = Slot(uri=CADSR.DataElementConcept, name="DataElement_DataElementConcept", curie=CADSR.curie('DataElementConcept'),
                   model_uri=CADSR.DataElement_DataElementConcept, domain=DataElement, range=Optional[Union[dict, "DataElementConcept"]])

slots.DataElement_ValueDomain = Slot(uri=CADSR.ValueDomain, name="DataElement_ValueDomain", curie=CADSR.curie('ValueDomain'),
                   model_uri=CADSR.DataElement_ValueDomain, domain=DataElement, range=Optional[Union[dict, "ValueDomain"]])

slots.DataElement_ClassificationSchemes = Slot(uri=CADSR.ClassificationSchemes, name="DataElement_ClassificationSchemes", curie=CADSR.curie('ClassificationSchemes'),
                   model_uri=CADSR.DataElement_ClassificationSchemes, domain=DataElement, range=Optional[Union[Union[dict, ClassificationScheme], List[Union[dict, ClassificationScheme]]]])

slots.DataElement_AlternateNames = Slot(uri=CADSR.AlternateNames, name="DataElement_AlternateNames", curie=CADSR.curie('AlternateNames'),
                   model_uri=CADSR.DataElement_AlternateNames, domain=DataElement, range=Optional[Union[Union[dict, AlternateName], List[Union[dict, AlternateName]]]])

slots.DataElement_ReferenceDocuments = Slot(uri=CADSR.ReferenceDocuments, name="DataElement_ReferenceDocuments", curie=CADSR.curie('ReferenceDocuments'),
                   model_uri=CADSR.DataElement_ReferenceDocuments, domain=DataElement, range=Optional[Union[Union[dict, "ReferenceDocument"], List[Union[dict, "ReferenceDocument"]]]])

slots.DataElement_origin = Slot(uri=CADSR.origin, name="DataElement_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.DataElement_origin, domain=DataElement, range=Optional[str])

slots.DataElement_workflowStatus = Slot(uri=CADSR.workflowStatus, name="DataElement_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.DataElement_workflowStatus, domain=DataElement, range=Optional[str])

slots.DataElement_registrationStatus = Slot(uri=CADSR.registrationStatus, name="DataElement_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.DataElement_registrationStatus, domain=DataElement, range=Optional[str])

slots.DataElement_id = Slot(uri=CADSR.id, name="DataElement_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.DataElement_id, domain=DataElement, range=Optional[str])

slots.DataElement_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="DataElement_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.DataElement_latestVersionIndicator, domain=DataElement, range=Optional[str])

slots.DataElement_beginDate = Slot(uri=CADSR.beginDate, name="DataElement_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.DataElement_beginDate, domain=DataElement, range=Optional[str])

slots.DataElement_endDate = Slot(uri=CADSR.endDate, name="DataElement_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.DataElement_endDate, domain=DataElement, range=Optional[str])

slots.DataElement_createdBy = Slot(uri=CADSR.createdBy, name="DataElement_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.DataElement_createdBy, domain=DataElement, range=Optional[str])

slots.DataElement_dateCreated = Slot(uri=CADSR.dateCreated, name="DataElement_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.DataElement_dateCreated, domain=DataElement, range=Optional[str])

slots.DataElement_modifiedBy = Slot(uri=CADSR.modifiedBy, name="DataElement_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.DataElement_modifiedBy, domain=DataElement, range=Optional[str])

slots.DataElement_dateModified = Slot(uri=CADSR.dateModified, name="DataElement_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.DataElement_dateModified, domain=DataElement, range=Optional[str])

slots.DataElement_changeDescription = Slot(uri=CADSR.changeDescription, name="DataElement_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.DataElement_changeDescription, domain=DataElement, range=Optional[str])

slots.DataElement_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="DataElement_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.DataElement_administrativeNotes, domain=DataElement, range=Optional[str])

slots.DataElement_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="DataElement_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.DataElement_unresolvedIssues, domain=DataElement, range=Optional[str])

slots.DataElement_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="DataElement_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.DataElement_deletedIndicator, domain=DataElement, range=Optional[str])

slots.ValueDomain_publicId = Slot(uri=CADSR.publicId, name="ValueDomain_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ValueDomain_publicId, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_version = Slot(uri=CADSR.version, name="ValueDomain_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ValueDomain_version, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_preferredName = Slot(uri=CADSR.preferredName, name="ValueDomain_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.ValueDomain_preferredName, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="ValueDomain_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.ValueDomain_preferredDefinition, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_longName = Slot(uri=CADSR.longName, name="ValueDomain_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ValueDomain_longName, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_context = Slot(uri=CADSR.context, name="ValueDomain_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ValueDomain_context, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_contextVersion = Slot(uri=CADSR.contextVersion, name="ValueDomain_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.ValueDomain_contextVersion, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_type = Slot(uri=CADSR.type, name="ValueDomain_type", curie=CADSR.curie('type'),
                   model_uri=CADSR.ValueDomain_type, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_dataType = Slot(uri=CADSR.dataType, name="ValueDomain_dataType", curie=CADSR.curie('dataType'),
                   model_uri=CADSR.ValueDomain_dataType, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_unitOfMeasure = Slot(uri=CADSR.unitOfMeasure, name="ValueDomain_unitOfMeasure", curie=CADSR.curie('unitOfMeasure'),
                   model_uri=CADSR.ValueDomain_unitOfMeasure, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_characterSet = Slot(uri=CADSR.characterSet, name="ValueDomain_characterSet", curie=CADSR.curie('characterSet'),
                   model_uri=CADSR.ValueDomain_characterSet, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_minLength = Slot(uri=CADSR.minLength, name="ValueDomain_minLength", curie=CADSR.curie('minLength'),
                   model_uri=CADSR.ValueDomain_minLength, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_maxLength = Slot(uri=CADSR.maxLength, name="ValueDomain_maxLength", curie=CADSR.curie('maxLength'),
                   model_uri=CADSR.ValueDomain_maxLength, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_minValue = Slot(uri=CADSR.minValue, name="ValueDomain_minValue", curie=CADSR.curie('minValue'),
                   model_uri=CADSR.ValueDomain_minValue, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_maxValue = Slot(uri=CADSR.maxValue, name="ValueDomain_maxValue", curie=CADSR.curie('maxValue'),
                   model_uri=CADSR.ValueDomain_maxValue, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_decimalPlace = Slot(uri=CADSR.decimalPlace, name="ValueDomain_decimalPlace", curie=CADSR.curie('decimalPlace'),
                   model_uri=CADSR.ValueDomain_decimalPlace, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_format = Slot(uri=CADSR.format, name="ValueDomain_format", curie=CADSR.curie('format'),
                   model_uri=CADSR.ValueDomain_format, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_PermissibleValues = Slot(uri=CADSR.PermissibleValues, name="ValueDomain_PermissibleValues", curie=CADSR.curie('PermissibleValues'),
                   model_uri=CADSR.ValueDomain_PermissibleValues, domain=ValueDomain, range=Optional[Union[Union[dict, "CDEPermissibleValue"], List[Union[dict, "CDEPermissibleValue"]]]])

slots.ValueDomain_ConceptualDomain = Slot(uri=CADSR.ConceptualDomain, name="ValueDomain_ConceptualDomain", curie=CADSR.curie('ConceptualDomain'),
                   model_uri=CADSR.ValueDomain_ConceptualDomain, domain=ValueDomain, range=Optional[Union[dict, ConceptualDomain]])

slots.ValueDomain_RepresentationTerm = Slot(uri=CADSR.RepresentationTerm, name="ValueDomain_RepresentationTerm", curie=CADSR.curie('RepresentationTerm'),
                   model_uri=CADSR.ValueDomain_RepresentationTerm, domain=ValueDomain, range=Optional[Union[dict, "RepresentationTerm"]])

slots.ValueDomain_origin = Slot(uri=CADSR.origin, name="ValueDomain_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.ValueDomain_origin, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_workflowStatus = Slot(uri=CADSR.workflowStatus, name="ValueDomain_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.ValueDomain_workflowStatus, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_registrationStatus = Slot(uri=CADSR.registrationStatus, name="ValueDomain_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.ValueDomain_registrationStatus, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_id = Slot(uri=CADSR.id, name="ValueDomain_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.ValueDomain_id, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="ValueDomain_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.ValueDomain_latestVersionIndicator, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_beginDate = Slot(uri=CADSR.beginDate, name="ValueDomain_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.ValueDomain_beginDate, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_endDate = Slot(uri=CADSR.endDate, name="ValueDomain_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.ValueDomain_endDate, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_createdBy = Slot(uri=CADSR.createdBy, name="ValueDomain_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.ValueDomain_createdBy, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_dateCreated = Slot(uri=CADSR.dateCreated, name="ValueDomain_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.ValueDomain_dateCreated, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_modifiedBy = Slot(uri=CADSR.modifiedBy, name="ValueDomain_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.ValueDomain_modifiedBy, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_dateModified = Slot(uri=CADSR.dateModified, name="ValueDomain_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.ValueDomain_dateModified, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_changeDescription = Slot(uri=CADSR.changeDescription, name="ValueDomain_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.ValueDomain_changeDescription, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="ValueDomain_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.ValueDomain_administrativeNotes, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="ValueDomain_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.ValueDomain_unresolvedIssues, domain=ValueDomain, range=Optional[str])

slots.ValueDomain_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="ValueDomain_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.ValueDomain_deletedIndicator, domain=ValueDomain, range=Optional[str])

slots.ObjectClass_publicId = Slot(uri=CADSR.publicId, name="ObjectClass_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ObjectClass_publicId, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_version = Slot(uri=CADSR.version, name="ObjectClass_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ObjectClass_version, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_preferredName = Slot(uri=CADSR.preferredName, name="ObjectClass_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.ObjectClass_preferredName, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="ObjectClass_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.ObjectClass_preferredDefinition, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_longName = Slot(uri=CADSR.longName, name="ObjectClass_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ObjectClass_longName, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_context = Slot(uri=CADSR.context, name="ObjectClass_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ObjectClass_context, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_contextVersion = Slot(uri=CADSR.contextVersion, name="ObjectClass_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.ObjectClass_contextVersion, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_Concepts = Slot(uri=CADSR.Concepts, name="ObjectClass_Concepts", curie=CADSR.curie('Concepts'),
                   model_uri=CADSR.ObjectClass_Concepts, domain=ObjectClass, range=Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]])

slots.ObjectClass_origin = Slot(uri=CADSR.origin, name="ObjectClass_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.ObjectClass_origin, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_workflowStatus = Slot(uri=CADSR.workflowStatus, name="ObjectClass_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.ObjectClass_workflowStatus, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_registrationStatus = Slot(uri=CADSR.registrationStatus, name="ObjectClass_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.ObjectClass_registrationStatus, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_id = Slot(uri=CADSR.id, name="ObjectClass_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.ObjectClass_id, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="ObjectClass_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.ObjectClass_latestVersionIndicator, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_beginDate = Slot(uri=CADSR.beginDate, name="ObjectClass_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.ObjectClass_beginDate, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_endDate = Slot(uri=CADSR.endDate, name="ObjectClass_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.ObjectClass_endDate, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_createdBy = Slot(uri=CADSR.createdBy, name="ObjectClass_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.ObjectClass_createdBy, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_dateCreated = Slot(uri=CADSR.dateCreated, name="ObjectClass_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.ObjectClass_dateCreated, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_modifiedBy = Slot(uri=CADSR.modifiedBy, name="ObjectClass_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.ObjectClass_modifiedBy, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_dateModified = Slot(uri=CADSR.dateModified, name="ObjectClass_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.ObjectClass_dateModified, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_changeDescription = Slot(uri=CADSR.changeDescription, name="ObjectClass_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.ObjectClass_changeDescription, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="ObjectClass_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.ObjectClass_administrativeNotes, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="ObjectClass_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.ObjectClass_unresolvedIssues, domain=ObjectClass, range=Optional[str])

slots.ObjectClass_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="ObjectClass_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.ObjectClass_deletedIndicator, domain=ObjectClass, range=Optional[str])

slots.DataElementquery_GET_response_numRecords = Slot(uri=CADSR.numRecords, name="DataElementquery_GET_response_numRecords", curie=CADSR.curie('numRecords'),
                   model_uri=CADSR.DataElementquery_GET_response_numRecords, domain=DataElementqueryGETResponse, range=Optional[str])

slots.DataElementquery_GET_response_DataElementQueryResults = Slot(uri=CADSR.DataElementQueryResults, name="DataElementquery_GET_response_DataElementQueryResults", curie=CADSR.curie('DataElementQueryResults'),
                   model_uri=CADSR.DataElementquery_GET_response_DataElementQueryResults, domain=DataElementqueryGETResponse, range=Optional[Union[Union[dict, "DataElementQuery"], List[Union[dict, "DataElementQuery"]]]])

slots.Concept_longName = Slot(uri=CADSR.longName, name="Concept_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.Concept_longName, domain=Concept, range=Optional[str])

slots.Concept_conceptCode = Slot(uri=CADSR.conceptCode, name="Concept_conceptCode", curie=CADSR.curie('conceptCode'),
                   model_uri=CADSR.Concept_conceptCode, domain=Concept, range=Optional[str])

slots.Concept_definition = Slot(uri=CADSR.definition, name="Concept_definition", curie=CADSR.curie('definition'),
                   model_uri=CADSR.Concept_definition, domain=Concept, range=Optional[str])

slots.Concept_evsSource = Slot(uri=CADSR.evsSource, name="Concept_evsSource", curie=CADSR.curie('evsSource'),
                   model_uri=CADSR.Concept_evsSource, domain=Concept, range=Optional[str])

slots.Concept_primaryIndicator = Slot(uri=CADSR.primaryIndicator, name="Concept_primaryIndicator", curie=CADSR.curie('primaryIndicator'),
                   model_uri=CADSR.Concept_primaryIndicator, domain=Concept, range=Optional[str])

slots.Concept_displayOrder = Slot(uri=CADSR.displayOrder, name="Concept_displayOrder", curie=CADSR.curie('displayOrder'),
                   model_uri=CADSR.Concept_displayOrder, domain=Concept, range=Optional[str])

slots.DataElementConcept_publicId = Slot(uri=CADSR.publicId, name="DataElementConcept_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.DataElementConcept_publicId, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_version = Slot(uri=CADSR.version, name="DataElementConcept_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.DataElementConcept_version, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_preferredName = Slot(uri=CADSR.preferredName, name="DataElementConcept_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.DataElementConcept_preferredName, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="DataElementConcept_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.DataElementConcept_preferredDefinition, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_longName = Slot(uri=CADSR.longName, name="DataElementConcept_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.DataElementConcept_longName, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_context = Slot(uri=CADSR.context, name="DataElementConcept_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.DataElementConcept_context, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_contextVersion = Slot(uri=CADSR.contextVersion, name="DataElementConcept_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.DataElementConcept_contextVersion, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_ObjectClass = Slot(uri=CADSR.ObjectClass, name="DataElementConcept_ObjectClass", curie=CADSR.curie('ObjectClass'),
                   model_uri=CADSR.DataElementConcept_ObjectClass, domain=DataElementConcept, range=Optional[Union[dict, ObjectClass]])

slots.DataElementConcept_Property = Slot(uri=CADSR.Property, name="DataElementConcept_Property", curie=CADSR.curie('Property'),
                   model_uri=CADSR.DataElementConcept_Property, domain=DataElementConcept, range=Optional[Union[dict, Property]])

slots.DataElementConcept_ConceptualDomain = Slot(uri=CADSR.ConceptualDomain, name="DataElementConcept_ConceptualDomain", curie=CADSR.curie('ConceptualDomain'),
                   model_uri=CADSR.DataElementConcept_ConceptualDomain, domain=DataElementConcept, range=Optional[Union[dict, ConceptualDomain]])

slots.DataElementConcept_origin = Slot(uri=CADSR.origin, name="DataElementConcept_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.DataElementConcept_origin, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_workflowStatus = Slot(uri=CADSR.workflowStatus, name="DataElementConcept_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.DataElementConcept_workflowStatus, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_registrationStatus = Slot(uri=CADSR.registrationStatus, name="DataElementConcept_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.DataElementConcept_registrationStatus, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_id = Slot(uri=CADSR.id, name="DataElementConcept_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.DataElementConcept_id, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="DataElementConcept_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.DataElementConcept_latestVersionIndicator, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_beginDate = Slot(uri=CADSR.beginDate, name="DataElementConcept_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.DataElementConcept_beginDate, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_endDate = Slot(uri=CADSR.endDate, name="DataElementConcept_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.DataElementConcept_endDate, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_createdBy = Slot(uri=CADSR.createdBy, name="DataElementConcept_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.DataElementConcept_createdBy, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_dateCreated = Slot(uri=CADSR.dateCreated, name="DataElementConcept_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.DataElementConcept_dateCreated, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_modifiedBy = Slot(uri=CADSR.modifiedBy, name="DataElementConcept_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.DataElementConcept_modifiedBy, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_dateModified = Slot(uri=CADSR.dateModified, name="DataElementConcept_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.DataElementConcept_dateModified, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_changeDescription = Slot(uri=CADSR.changeDescription, name="DataElementConcept_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.DataElementConcept_changeDescription, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="DataElementConcept_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.DataElementConcept_administrativeNotes, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="DataElementConcept_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.DataElementConcept_unresolvedIssues, domain=DataElementConcept, range=Optional[str])

slots.DataElementConcept_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="DataElementConcept_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.DataElementConcept_deletedIndicator, domain=DataElementConcept, range=Optional[str])

slots.ValueMeaning_publicId = Slot(uri=CADSR.publicId, name="ValueMeaning_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.ValueMeaning_publicId, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_version = Slot(uri=CADSR.version, name="ValueMeaning_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.ValueMeaning_version, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_preferredName = Slot(uri=CADSR.preferredName, name="ValueMeaning_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.ValueMeaning_preferredName, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_longName = Slot(uri=CADSR.longName, name="ValueMeaning_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.ValueMeaning_longName, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="ValueMeaning_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.ValueMeaning_preferredDefinition, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_context = Slot(uri=CADSR.context, name="ValueMeaning_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ValueMeaning_context, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_contextVersion = Slot(uri=CADSR.contextVersion, name="ValueMeaning_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.ValueMeaning_contextVersion, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_Concepts = Slot(uri=CADSR.Concepts, name="ValueMeaning_Concepts", curie=CADSR.curie('Concepts'),
                   model_uri=CADSR.ValueMeaning_Concepts, domain=ValueMeaning, range=Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]])

slots.ValueMeaning_origin = Slot(uri=CADSR.origin, name="ValueMeaning_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.ValueMeaning_origin, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_workflowStatus = Slot(uri=CADSR.workflowStatus, name="ValueMeaning_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.ValueMeaning_workflowStatus, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_registrationStatus = Slot(uri=CADSR.registrationStatus, name="ValueMeaning_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.ValueMeaning_registrationStatus, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_id = Slot(uri=CADSR.id, name="ValueMeaning_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.ValueMeaning_id, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="ValueMeaning_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.ValueMeaning_latestVersionIndicator, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_beginDate = Slot(uri=CADSR.beginDate, name="ValueMeaning_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.ValueMeaning_beginDate, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_endDate = Slot(uri=CADSR.endDate, name="ValueMeaning_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.ValueMeaning_endDate, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_createdBy = Slot(uri=CADSR.createdBy, name="ValueMeaning_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.ValueMeaning_createdBy, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_dateCreated = Slot(uri=CADSR.dateCreated, name="ValueMeaning_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.ValueMeaning_dateCreated, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_modifiedBy = Slot(uri=CADSR.modifiedBy, name="ValueMeaning_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.ValueMeaning_modifiedBy, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_dateModified = Slot(uri=CADSR.dateModified, name="ValueMeaning_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.ValueMeaning_dateModified, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_changeDescription = Slot(uri=CADSR.changeDescription, name="ValueMeaning_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.ValueMeaning_changeDescription, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="ValueMeaning_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.ValueMeaning_administrativeNotes, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="ValueMeaning_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.ValueMeaning_unresolvedIssues, domain=ValueMeaning, range=Optional[str])

slots.ValueMeaning_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="ValueMeaning_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.ValueMeaning_deletedIndicator, domain=ValueMeaning, range=Optional[str])

slots.RepresentationTerm_publicId = Slot(uri=CADSR.publicId, name="RepresentationTerm_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.RepresentationTerm_publicId, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_version = Slot(uri=CADSR.version, name="RepresentationTerm_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.RepresentationTerm_version, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_preferredName = Slot(uri=CADSR.preferredName, name="RepresentationTerm_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.RepresentationTerm_preferredName, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="RepresentationTerm_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.RepresentationTerm_preferredDefinition, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_longName = Slot(uri=CADSR.longName, name="RepresentationTerm_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.RepresentationTerm_longName, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_context = Slot(uri=CADSR.context, name="RepresentationTerm_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.RepresentationTerm_context, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_contextVersion = Slot(uri=CADSR.contextVersion, name="RepresentationTerm_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.RepresentationTerm_contextVersion, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_Concepts = Slot(uri=CADSR.Concepts, name="RepresentationTerm_Concepts", curie=CADSR.curie('Concepts'),
                   model_uri=CADSR.RepresentationTerm_Concepts, domain=RepresentationTerm, range=Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]])

slots.RepresentationTerm_origin = Slot(uri=CADSR.origin, name="RepresentationTerm_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.RepresentationTerm_origin, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_workflowStatus = Slot(uri=CADSR.workflowStatus, name="RepresentationTerm_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.RepresentationTerm_workflowStatus, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_registrationStatus = Slot(uri=CADSR.registrationStatus, name="RepresentationTerm_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.RepresentationTerm_registrationStatus, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_id = Slot(uri=CADSR.id, name="RepresentationTerm_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.RepresentationTerm_id, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="RepresentationTerm_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.RepresentationTerm_latestVersionIndicator, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_beginDate = Slot(uri=CADSR.beginDate, name="RepresentationTerm_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.RepresentationTerm_beginDate, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_endDate = Slot(uri=CADSR.endDate, name="RepresentationTerm_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.RepresentationTerm_endDate, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_createdBy = Slot(uri=CADSR.createdBy, name="RepresentationTerm_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.RepresentationTerm_createdBy, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_dateCreated = Slot(uri=CADSR.dateCreated, name="RepresentationTerm_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.RepresentationTerm_dateCreated, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_modifiedBy = Slot(uri=CADSR.modifiedBy, name="RepresentationTerm_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.RepresentationTerm_modifiedBy, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_dateModified = Slot(uri=CADSR.dateModified, name="RepresentationTerm_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.RepresentationTerm_dateModified, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_changeDescription = Slot(uri=CADSR.changeDescription, name="RepresentationTerm_changeDescription", curie=CADSR.curie('changeDescription'),
                   model_uri=CADSR.RepresentationTerm_changeDescription, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="RepresentationTerm_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.RepresentationTerm_administrativeNotes, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="RepresentationTerm_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.RepresentationTerm_unresolvedIssues, domain=RepresentationTerm, range=Optional[str])

slots.RepresentationTerm_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="RepresentationTerm_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.RepresentationTerm_deletedIndicator, domain=RepresentationTerm, range=Optional[str])

slots.ReferenceDocument_type = Slot(uri=CADSR.type, name="ReferenceDocument_type", curie=CADSR.curie('type'),
                   model_uri=CADSR.ReferenceDocument_type, domain=ReferenceDocument, range=Optional[str])

slots.ReferenceDocument_description = Slot(uri=CADSR.description, name="ReferenceDocument_description", curie=CADSR.curie('description'),
                   model_uri=CADSR.ReferenceDocument_description, domain=ReferenceDocument, range=Optional[str])

slots.ReferenceDocument_url = Slot(uri=CADSR.url, name="ReferenceDocument_url", curie=CADSR.curie('url'),
                   model_uri=CADSR.ReferenceDocument_url, domain=ReferenceDocument, range=Optional[str])

slots.ReferenceDocument_context = Slot(uri=CADSR.context, name="ReferenceDocument_context", curie=CADSR.curie('context'),
                   model_uri=CADSR.ReferenceDocument_context, domain=ReferenceDocument, range=Optional[str])

slots.CDEPermissibleValue_publicId = Slot(uri=CADSR.publicId, name="CDEPermissibleValue_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.CDEPermissibleValue_publicId, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_value = Slot(uri=CADSR.value, name="CDEPermissibleValue_value", curie=CADSR.curie('value'),
                   model_uri=CADSR.CDEPermissibleValue_value, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_valueDescription = Slot(uri=CADSR.valueDescription, name="CDEPermissibleValue_valueDescription", curie=CADSR.curie('valueDescription'),
                   model_uri=CADSR.CDEPermissibleValue_valueDescription, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_ValueMeaning = Slot(uri=CADSR.ValueMeaning, name="CDEPermissibleValue_ValueMeaning", curie=CADSR.curie('ValueMeaning'),
                   model_uri=CADSR.CDEPermissibleValue_ValueMeaning, domain=CDEPermissibleValue, range=Optional[Union[dict, ValueMeaning]])

slots.CDEPermissibleValue_origin = Slot(uri=CADSR.origin, name="CDEPermissibleValue_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.CDEPermissibleValue_origin, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_id = Slot(uri=CADSR.id, name="CDEPermissibleValue_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.CDEPermissibleValue_id, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_beginDate = Slot(uri=CADSR.beginDate, name="CDEPermissibleValue_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.CDEPermissibleValue_beginDate, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_endDate = Slot(uri=CADSR.endDate, name="CDEPermissibleValue_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.CDEPermissibleValue_endDate, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_createdBy = Slot(uri=CADSR.createdBy, name="CDEPermissibleValue_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.CDEPermissibleValue_createdBy, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_dateCreated = Slot(uri=CADSR.dateCreated, name="CDEPermissibleValue_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.CDEPermissibleValue_dateCreated, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_modifiedBy = Slot(uri=CADSR.modifiedBy, name="CDEPermissibleValue_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.CDEPermissibleValue_modifiedBy, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_dateModified = Slot(uri=CADSR.dateModified, name="CDEPermissibleValue_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.CDEPermissibleValue_dateModified, domain=CDEPermissibleValue, range=Optional[str])

slots.CDEPermissibleValue_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="CDEPermissibleValue_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.CDEPermissibleValue_deletedIndicator, domain=CDEPermissibleValue, range=Optional[str])

slots.DataElementQuery_publicId = Slot(uri=CADSR.publicId, name="DataElementQuery_publicId", curie=CADSR.curie('publicId'),
                   model_uri=CADSR.DataElementQuery_publicId, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_version = Slot(uri=CADSR.version, name="DataElementQuery_version", curie=CADSR.curie('version'),
                   model_uri=CADSR.DataElementQuery_version, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_preferredName = Slot(uri=CADSR.preferredName, name="DataElementQuery_preferredName", curie=CADSR.curie('preferredName'),
                   model_uri=CADSR.DataElementQuery_preferredName, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_preferredDefinition = Slot(uri=CADSR.preferredDefinition, name="DataElementQuery_preferredDefinition", curie=CADSR.curie('preferredDefinition'),
                   model_uri=CADSR.DataElementQuery_preferredDefinition, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_longName = Slot(uri=CADSR.longName, name="DataElementQuery_longName", curie=CADSR.curie('longName'),
                   model_uri=CADSR.DataElementQuery_longName, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_contextName = Slot(uri=CADSR.contextName, name="DataElementQuery_contextName", curie=CADSR.curie('contextName'),
                   model_uri=CADSR.DataElementQuery_contextName, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_contextVersion = Slot(uri=CADSR.contextVersion, name="DataElementQuery_contextVersion", curie=CADSR.curie('contextVersion'),
                   model_uri=CADSR.DataElementQuery_contextVersion, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_dataElementConceptPublicId = Slot(uri=CADSR.dataElementConceptPublicId, name="DataElementQuery_dataElementConceptPublicId", curie=CADSR.curie('dataElementConceptPublicId'),
                   model_uri=CADSR.DataElementQuery_dataElementConceptPublicId, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_dataElementConceptVersion = Slot(uri=CADSR.dataElementConceptVersion, name="DataElementQuery_dataElementConceptVersion", curie=CADSR.curie('dataElementConceptVersion'),
                   model_uri=CADSR.DataElementQuery_dataElementConceptVersion, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_valueDomainPublicId = Slot(uri=CADSR.valueDomainPublicId, name="DataElementQuery_valueDomainPublicId", curie=CADSR.curie('valueDomainPublicId'),
                   model_uri=CADSR.DataElementQuery_valueDomainPublicId, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_valueDomainVersion = Slot(uri=CADSR.valueDomainVersion, name="DataElementQuery_valueDomainVersion", curie=CADSR.curie('valueDomainVersion'),
                   model_uri=CADSR.DataElementQuery_valueDomainVersion, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_origin = Slot(uri=CADSR.origin, name="DataElementQuery_origin", curie=CADSR.curie('origin'),
                   model_uri=CADSR.DataElementQuery_origin, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_workflowStatus = Slot(uri=CADSR.workflowStatus, name="DataElementQuery_workflowStatus", curie=CADSR.curie('workflowStatus'),
                   model_uri=CADSR.DataElementQuery_workflowStatus, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_registrationStatus = Slot(uri=CADSR.registrationStatus, name="DataElementQuery_registrationStatus", curie=CADSR.curie('registrationStatus'),
                   model_uri=CADSR.DataElementQuery_registrationStatus, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_id = Slot(uri=CADSR.id, name="DataElementQuery_id", curie=CADSR.curie('id'),
                   model_uri=CADSR.DataElementQuery_id, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_latestVersionIndicator = Slot(uri=CADSR.latestVersionIndicator, name="DataElementQuery_latestVersionIndicator", curie=CADSR.curie('latestVersionIndicator'),
                   model_uri=CADSR.DataElementQuery_latestVersionIndicator, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_beginDate = Slot(uri=CADSR.beginDate, name="DataElementQuery_beginDate", curie=CADSR.curie('beginDate'),
                   model_uri=CADSR.DataElementQuery_beginDate, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_endDate = Slot(uri=CADSR.endDate, name="DataElementQuery_endDate", curie=CADSR.curie('endDate'),
                   model_uri=CADSR.DataElementQuery_endDate, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_createdBy = Slot(uri=CADSR.createdBy, name="DataElementQuery_createdBy", curie=CADSR.curie('createdBy'),
                   model_uri=CADSR.DataElementQuery_createdBy, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_dateCreated = Slot(uri=CADSR.dateCreated, name="DataElementQuery_dateCreated", curie=CADSR.curie('dateCreated'),
                   model_uri=CADSR.DataElementQuery_dateCreated, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_modifiedBy = Slot(uri=CADSR.modifiedBy, name="DataElementQuery_modifiedBy", curie=CADSR.curie('modifiedBy'),
                   model_uri=CADSR.DataElementQuery_modifiedBy, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_dateModified = Slot(uri=CADSR.dateModified, name="DataElementQuery_dateModified", curie=CADSR.curie('dateModified'),
                   model_uri=CADSR.DataElementQuery_dateModified, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_changeNote = Slot(uri=CADSR.changeNote, name="DataElementQuery_changeNote", curie=CADSR.curie('changeNote'),
                   model_uri=CADSR.DataElementQuery_changeNote, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_administrativeNotes = Slot(uri=CADSR.administrativeNotes, name="DataElementQuery_administrativeNotes", curie=CADSR.curie('administrativeNotes'),
                   model_uri=CADSR.DataElementQuery_administrativeNotes, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_unresolvedIssues = Slot(uri=CADSR.unresolvedIssues, name="DataElementQuery_unresolvedIssues", curie=CADSR.curie('unresolvedIssues'),
                   model_uri=CADSR.DataElementQuery_unresolvedIssues, domain=DataElementQuery, range=Optional[str])

slots.DataElementQuery_deletedIndicator = Slot(uri=CADSR.deletedIndicator, name="DataElementQuery_deletedIndicator", curie=CADSR.curie('deletedIndicator'),
                   model_uri=CADSR.DataElementQuery_deletedIndicator, domain=DataElementQuery, range=Optional[str])

slots.permissibleValue_Permissible_Value = Slot(uri=CADSR.Permissible_Value, name="permissibleValue_Permissible Value", curie=CADSR.curie('Permissible_Value'),
                   model_uri=CADSR.permissibleValue_Permissible_Value, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_VM_Long_Name = Slot(uri=CADSR.VM_Long_Name, name="permissibleValue_VM Long Name", curie=CADSR.curie('VM_Long_Name'),
                   model_uri=CADSR.permissibleValue_VM_Long_Name, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_VM_Public_ID = Slot(uri=CADSR.VM_Public_ID, name="permissibleValue_VM Public ID", curie=CADSR.curie('VM_Public_ID'),
                   model_uri=CADSR.permissibleValue_VM_Public_ID, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_Concept_Code = Slot(uri=CADSR.Concept_Code, name="permissibleValue_Concept Code", curie=CADSR.curie('Concept_Code'),
                   model_uri=CADSR.permissibleValue_Concept_Code, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_VM_Description = Slot(uri=CADSR.VM_Description, name="permissibleValue_VM Description", curie=CADSR.curie('VM_Description'),
                   model_uri=CADSR.permissibleValue_VM_Description, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_Begin_Date = Slot(uri=CADSR.Begin_Date, name="permissibleValue_Begin Date", curie=CADSR.curie('Begin_Date'),
                   model_uri=CADSR.permissibleValue_Begin_Date, domain=PermissibleValue, range=Optional[str])

slots.permissibleValue_End_Date = Slot(uri=CADSR.End_Date, name="permissibleValue_End Date", curie=CADSR.curie('End_Date'),
                   model_uri=CADSR.permissibleValue_End_Date, domain=PermissibleValue, range=Optional[str])
