"""EML (Ecological Metadata Language) XML → LinkML schema importer.

Uses a load+map+dump pipeline:

1. ``schema_automator.loaders.xml_loader`` parses EML XML against the
   :doc:`metamodels/eml.yaml` source schema.
2. The linkml-map trans-spec at
   ``schema_automator/importers/eml_to_linkml.transform.yaml`` maps
   each EML class to its LinkML meta-schema counterpart
   (``EMLDocument → schema_definition``, ``DataTable → class_definition``,
   ``Attribute → slot_definition``).
3. Python in :meth:`EmlImportEngine.convert` orchestrates iteration
   over inlined nested collections (``dataset.dataTable[]`` and
   ``attributeList.attribute[]``). linkml-map's ``populated_from``
   currently walks FK joins via ``ObjectIndex`` rather than inlined
   hierarchy, so the trans-spec stays to single-level class
   derivations and Python drives the descent.

Open gaps tracked upstream — see comments in the trans-spec YAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from linkml_map.transformer.object_transformer import ObjectTransformer
from linkml_map.utils.loaders import load_specification
from linkml_runtime.linkml_model.meta import SchemaDefinition
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.importers.import_engine import ImportEngine
from schema_automator.loaders.xml_loader import XMLLoader

_PKG_ROOT = Path(__file__).resolve().parents[1]
_EML_SCHEMA = _PKG_ROOT / "metamodels" / "eml.yaml"
_TRANS_SPEC = Path(__file__).resolve().parent / "eml_to_linkml.transform.yaml"


@lru_cache(maxsize=1)
def _eml_schemaview() -> SchemaView:
    """Cached SchemaView for the EML source schema (thread-safe under the GIL)."""
    return SchemaView(str(_EML_SCHEMA))


@lru_cache(maxsize=1)
def _eml_specification() -> Any:
    return load_specification(str(_TRANS_SPEC))


@dataclass
class EmlImportEngine(ImportEngine):
    """Importer for EML XML documents (EML 2.2.0).

    Produces a :class:`SchemaDefinition` whose classes correspond to
    EML ``<dataTable>`` blocks and whose attributes correspond to EML
    ``<attribute>`` children. Measurement-scale variants
    (``nominal``/``ordinal``/``interval``/``ratio``/``dateTime``) map
    to LinkML ranges (``string``/``integer``/``float``) via the
    trans-spec.

    Not yet handled (tracked via linkml-map upstream issues):
        * ``<enumeratedDomain>`` slots — currently degrade to
          ``range: string`` because emitting a co-named
          ``enum_definition`` from one source ``<attribute>`` requires
          linkml-map#239 (multi-artifact emission) and linkml-map#237
          (cross-class references).
        * Unit metadata on numeric scales — captured in EML's
          ``<unit><standardUnit>``/``<customUnit>`` but not surfaced as
          LinkML annotations or constraints in v1.
        * Format-string metadata on dateTime scales — captured in
          ``<formatString>`` but not surfaced beyond ``range: string``.
    """

    def convert(self, file: str, **kwargs: Any) -> SchemaDefinition:
        """Parse an EML document and return a LinkML SchemaDefinition.

        :param file: Path to an EML XML document.
        :returns: A SchemaDefinition with one class per ``<dataTable>``
            and one attribute per ``<attribute>``.
        """
        src = self._load(Path(file))
        target = self._transform(src)
        return self._materialize(target)

    def _load(self, path: Path) -> dict:
        return XMLLoader().load_as_dict(
            source=path,
            target_class="EMLDocument",
            schemaview=_eml_schemaview(),
        )

    def _transform(self, src: dict) -> dict:
        tr = ObjectTransformer(
            source_schemaview=_eml_schemaview(),
            specification=_eml_specification(),
        )
        schema = tr.map_object(src, source_type="EMLDocument")
        schema["classes"] = {}
        # Track sanitized → source name to surface collisions explicitly
        # instead of silently overwriting. The replace-chain in the
        # trans-spec is lossy (e.g. parens, commas, slashes all fold to
        # underscores or nothing), so distinct EML names with only
        # punctuation differences can collide.
        seen_classes: dict[str, str] = {}
        for dt in (src.get("dataset") or {}).get("dataTable", []):
            cls = tr.map_object(dt, source_type="DataTable")
            cls_name = cls.get("name")
            if cls_name:
                if cls_name in seen_classes:
                    raise ValueError(
                        f"EML name collision: both "
                        f"{seen_classes[cls_name]!r} and "
                        f"{dt.get('entityName')!r} sanitize to "
                        f"{cls_name!r}. Rename one of the entities in "
                        f"the source EML, or wait for upstream slugify "
                        f"support (linkml/linkml-map#242)."
                    )
                seen_classes[cls_name] = dt.get("entityName")
            cls["attributes"] = {}
            seen_attrs: dict[str, str] = {}
            for attr in (dt.get("attributeList") or {}).get("attribute", []):
                slot = tr.map_object(attr, source_type="Attribute")
                slot_name = slot.get("name")
                if slot_name:
                    if slot_name in seen_attrs:
                        raise ValueError(
                            f"EML name collision in dataTable "
                            f"{dt.get('entityName')!r}: both "
                            f"{seen_attrs[slot_name]!r} and "
                            f"{attr.get('attributeName')!r} sanitize "
                            f"to {slot_name!r}. Rename one of the "
                            f"attributes in the source EML, or wait "
                            f"for upstream slugify support "
                            f"(linkml/linkml-map#242)."
                        )
                    seen_attrs[slot_name] = attr.get("attributeName")
                    cls["attributes"][slot_name] = slot
            if cls_name:
                schema["classes"][cls_name] = cls
        return schema

    def _materialize(self, d: dict) -> SchemaDefinition:
        return SchemaDefinition(**{k: v for k, v in d.items() if v is not None})
