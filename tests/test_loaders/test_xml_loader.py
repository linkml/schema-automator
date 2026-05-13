"""Tests for the schema-driven XML loader."""

from pathlib import Path
from textwrap import dedent

import pytest
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.loaders.xml_loader import XMLLoadErrors, xml_loader


_FIXTURES = Path(__file__).resolve().parents[1] / "resources" / "dbgap"
_JHS_DD = _FIXTURES / "JHS_Subject.data_dict.xml"


# ----------------------------------------------------------------------
# Real-fixture: load JHS_Subject.data_dict.xml against the dbGaP schema
# ----------------------------------------------------------------------


class TestDbgapDataDict:
    """Exercise the loader against a real dbGaP data_dict.xml.

    Uses the existing dbGaP schema and fixture; these test cases are
    the loader's load-bearing real-world workout.
    """

    @pytest.fixture(scope="class")
    def result(self):
        pkg_root = Path(__file__).resolve().parents[2] / "schema_automator"
        sv = SchemaView(str(pkg_root / "metamodels" / "dbgap.yaml"))
        return xml_loader.load_as_dict(
            _JHS_DD, target_class="VariableDigest", schemaview=sv
        )

    def test_top_level_attributes(self, result):
        # data_table_id is annotated as xml_attribute: id (named override).
        assert result["data_table_id"] == "pht001920.v6"
        # study_id is annotated as xml_attribute: true (slot-name match).
        assert result["study_id"] == "phs000286.v7"
        assert result["participant_set"] == "2"
        assert result["date_created"] == "Wed Jul  3 10:11:42 2024"

    def test_empty_description_element_yields_none(self, result):
        # <description/> is empty; the loader returns None, not "".
        assert result["description"] is None

    def test_variables_count(self, result):
        # variables slot is annotated xml_element: variable; multivalued
        # picks up each <variable> child.
        assert len(result["variables"]) == 7

    def test_variable_attribute(self, result):
        # id is annotated xml_attribute: true on Variable.
        first = result["variables"][0]
        assert first["id"] == "phv00124545.v4"

    def test_variable_child_elements(self, result):
        # name, description map by default (slot name = element tag).
        first = result["variables"][0]
        assert first["name"] == "SUBJECT_ID"
        assert first["description"] == "Subject ID"

    def test_variable_element_name_override(self, result):
        # reported_type is annotated xml_element: type — slot name differs
        # from element name.
        first = result["variables"][0]
        assert first["reported_type"] == "String"

    def test_encoded_values(self, result):
        # CONSENT has <value code="N">label</value> children.
        # values is multivalued xml_element: value, range EncodedValue.
        consent = next(v for v in result["variables"] if v["name"] == "CONSENT")
        codes = consent["values"]
        assert len(codes) == 5
        # EncodedValue.code is xml_attribute: true
        # EncodedValue.label is xml_text: true
        c0 = codes[0]
        assert c0["code"] == "0"
        assert "did not participate" in c0["label"]

    def test_multivalued_empty_when_absent(self, result):
        # SUBJECT_ID has no <value> children; values should be [], not absent.
        subject_id = next(v for v in result["variables"] if v["name"] == "SUBJECT_ID")
        assert subject_id["values"] == []

    def test_label_with_commas_preserved_verbatim(self, result):
        # The xml_text annotation should give us the raw text content,
        # including commas and parens — no _sanitize_label-style mangling.
        consent = next(v for v in result["variables"] if v["name"] == "CONSENT")
        irb_npu = next(c for c in consent["values"] if c["code"] == "1")
        assert "(IRB, NPU)" in irb_npu["label"]


# ----------------------------------------------------------------------
# Synthetic small schemas exercising specific conventions
# ----------------------------------------------------------------------


@pytest.fixture
def make_schema(tmp_path):
    """Helper to spin up tiny LinkML schemas in tmp."""

    def _make(body: str) -> SchemaView:
        path = tmp_path / "schema.yaml"
        path.write_text(dedent(body).strip() + "\n")
        return SchemaView(str(path))

    return _make


class TestXmlAttribute:
    def test_attribute_with_explicit_name(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes:
              linkml: https://w3id.org/linkml/
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  display_id:
                    range: string
                    annotations:
                      xml_attribute: id
            """
        )
        result = xml_loader.load_as_dict(
            '<thing id="X1"/>', target_class="Thing", schemaview=sv
        )
        assert result == {"display_id": "X1"}

    def test_attribute_with_bare_true(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        result = xml_loader.load_as_dict(
            '<thing code="42"/>', target_class="Thing", schemaview=sv
        )
        assert result == {"code": "42"}


class TestXmlText:
    def test_text_content_in_leaf(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  label:
                    range: string
                    annotations:
                      xml_text: true
            """
        )
        result = xml_loader.load_as_dict(
            "<thing>hello world</thing>", target_class="Thing", schemaview=sv
        )
        assert result == {"label": "hello world"}

    def test_text_content_with_sibling_attribute(self, make_schema):
        # Mixed: a single element with BOTH an attribute and text content.
        # This is the dbGaP <value code="X">label</value> pattern.
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              CodedValue:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
                  label:
                    range: string
                    annotations:
                      xml_text: true
            """
        )
        result = xml_loader.load_as_dict(
            '<value code="1">Yes</value>',
            target_class="CodedValue",
            schemaview=sv,
        )
        assert result == {"code": "1", "label": "Yes"}


class TestMultivalued:
    def test_repeated_children_collected_as_list(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Bag:
                attributes:
                  items:
                    range: string
                    multivalued: true
                    annotations:
                      xml_element: item
            """
        )
        result = xml_loader.load_as_dict(
            "<bag><item>a</item><item>b</item><item>c</item></bag>",
            target_class="Bag",
            schemaview=sv,
        )
        assert result == {"items": ["a", "b", "c"]}

    def test_empty_multivalued_yields_empty_list(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Bag:
                attributes:
                  items:
                    range: string
                    multivalued: true
                    annotations:
                      xml_element: item
            """
        )
        result = xml_loader.load_as_dict(
            "<bag/>", target_class="Bag", schemaview=sv
        )
        assert result == {"items": []}


class TestXmlPath:
    def test_path_attribute(self, make_schema):
        # The dbGaP var_report case: deeply nested attribute.
        # <variable><total><stats><stat min="18"/></stats></total></variable>
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  min:
                    range: string
                    annotations:
                      xml_path: total/stats/stat/@min
                  max:
                    range: string
                    annotations:
                      xml_path: total/stats/stat/@max
            """
        )
        xml = """
          <variable>
            <total><stats><stat min="18" max="89"/></stats></total>
          </variable>
        """.strip()
        result = xml_loader.load_as_dict(
            xml, target_class="Variable", schemaview=sv
        )
        assert result == {"min": "18", "max": "89"}

    def test_path_text_content(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  unit_label:
                    range: string
                    annotations:
                      xml_path: meta/units/label
            """
        )
        xml = "<variable><meta><units><label>kg</label></units></meta></variable>"
        result = xml_loader.load_as_dict(
            xml, target_class="Variable", schemaview=sv
        )
        assert result == {"unit_label": "kg"}

    def test_path_missing_yields_none(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  min:
                    range: string
                    annotations:
                      xml_path: total/stats/stat/@min
            """
        )
        result = xml_loader.load_as_dict(
            "<variable/>", target_class="Variable", schemaview=sv
        )
        assert result == {}


class TestSourceInputs:
    """Loader should accept paths, file handles, and inline strings."""

    def test_load_from_path(self, make_schema, tmp_path):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        xml_path = tmp_path / "thing.xml"
        xml_path.write_text('<thing code="42"/>')
        result = xml_loader.load_as_dict(
            xml_path, target_class="Thing", schemaview=sv
        )
        assert result == {"code": "42"}

    def test_load_from_string(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        result = xml_loader.load_as_dict(
            '<thing code="42"/>', target_class="Thing", schemaview=sv
        )
        assert result == {"code": "42"}


class TestErrors:
    def test_unknown_class_raises(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes: {}
            """
        )
        with pytest.raises(ValueError, match="not in schema"):
            xml_loader.load_as_dict(
                "<thing/>", target_class="NotAClass", schemaview=sv
            )

    def test_missing_schemaview_raises(self):
        with pytest.raises(ValueError, match="schemaview"):
            xml_loader.load_as_dict("<thing/>", target_class="Thing")

    def test_missing_target_class_raises(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing: {}
            """
        )
        with pytest.raises(ValueError, match="target_class"):
            xml_loader.load_as_dict("<thing/>", schemaview=sv)


class TestNamespaces:
    """Loose-match by local name for namespaced tags + attributes."""

    def test_namespaced_element_matches_local_name(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  label:
                    range: string
                    annotations:
                      xml_element: name
            """
        )
        xml = '<thing xmlns:ns="http://example.org/ns"><ns:name>Bob</ns:name></thing>'
        result = xml_loader.load_as_dict(
            xml, target_class="Thing", schemaview=sv
        )
        assert result == {"label": "Bob"}

    def test_xsi_type_attribute_matches_as_type(self, make_schema):
        # xsi:type is the most common namespaced attribute in real-world
        # XML. Local-name matching should let it bind to a slot annotated
        # `xml_attribute: type` without the schema author needing to
        # declare the xsi namespace.
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  kind:
                    range: string
                    annotations:
                      xml_attribute: type
            """
        )
        xml = (
            '<thing xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:type="example"/>'
        )
        result = xml_loader.load_as_dict(
            xml, target_class="Thing", schemaview=sv
        )
        assert result == {"kind": "example"}


class TestRootValidation:
    """Class-level `xml_element` annotation drives root-tag check."""

    def _schema_with_root(self, make_schema, root_name: str) -> SchemaView:
        return make_schema(
            f"""
            id: https://example.org/t
            name: t
            prefixes: {{linkml: https://w3id.org/linkml/}}
            imports: [linkml:types]
            classes:
              Root:
                annotations:
                  xml_element: {root_name}
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )

    def test_root_matches_lenient_default(self, make_schema):
        sv = self._schema_with_root(make_schema, "expected_root")
        # Wrong root: default mode silently parses anyway (debug-logs).
        result = xml_loader.load_as_dict(
            '<wrong_root code="X"/>', target_class="Root", schemaview=sv
        )
        assert result == {"code": "X"}

    def test_root_mismatch_strict_raises(self, make_schema):
        sv = self._schema_with_root(make_schema, "expected_root")
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                '<wrong_root code="X"/>',
                target_class="Root",
                schemaview=sv,
                strict=True,
            )
        msg = str(excinfo.value)
        assert "wrong_root" in msg
        assert "expected_root" in msg

    def test_root_match_passes_strict(self, make_schema):
        sv = self._schema_with_root(make_schema, "expected_root")
        result = xml_loader.load_as_dict(
            '<expected_root code="X"/>',
            target_class="Root",
            schemaview=sv,
            strict=True,
        )
        assert result == {"code": "X"}


class TestStrictMode:
    """Collect-all-and-report semantics for unmapped XML content."""

    def test_default_lenient_silently_drops_unknown_element(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  known:
                    range: string
            """
        )
        result = xml_loader.load_as_dict(
            "<root><known>x</known><unknown>y</unknown></root>",
            target_class="Root",
            schemaview=sv,
        )
        # No raise, unknown is dropped, known is preserved.
        assert result == {"known": "x"}

    def test_strict_raises_on_unknown_element(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  known:
                    range: string
            """
        )
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                "<root><known>x</known><unknown>y</unknown></root>",
                target_class="Root",
                schemaview=sv,
                strict=True,
            )
        msg = str(excinfo.value)
        assert "unknown" in msg
        # Path context should be present
        assert "/root" in msg

    def test_strict_raises_on_unknown_attribute(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  known:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                '<root known="x" weird="y"/>',
                target_class="Root",
                schemaview=sv,
                strict=True,
            )
        assert "weird" in str(excinfo.value)

    def test_strict_collects_all_errors(self, make_schema):
        """Multiple unmapped issues are aggregated into one exception."""
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  known:
                    range: string
            """
        )
        xml = (
            "<root><known>x</known>"
            "<bad_one>a</bad_one>"
            "<bad_two>b</bad_two>"
            "<bad_three>c</bad_three>"
            "</root>"
        )
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                xml, target_class="Root", schemaview=sv, strict=True
            )
        # All three reported, not just the first.
        assert len(excinfo.value.errors) == 3
        joined = "\n".join(excinfo.value.errors)
        assert "bad_one" in joined
        assert "bad_two" in joined
        assert "bad_three" in joined

    def test_strict_collects_errors_across_nested_classes(self, make_schema):
        """Path context should reflect nested element location."""
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  child:
                    range: Child
              Child:
                attributes:
                  known:
                    range: string
            """
        )
        xml = "<root><child><known>x</known><unknown>y</unknown></child></root>"
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                xml, target_class="Root", schemaview=sv, strict=True
            )
        assert len(excinfo.value.errors) == 1
        # Path should include the nesting.
        assert "/root/child" in excinfo.value.errors[0]
        assert "unknown" in excinfo.value.errors[0]

    def test_strict_clean_document_no_raise(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                attributes:
                  known:
                    range: string
            """
        )
        result = xml_loader.load_as_dict(
            "<root><known>x</known></root>",
            target_class="Root",
            schemaview=sv,
            strict=True,
        )
        assert result == {"known": "x"}

    def test_strict_aggregates_root_and_content_errors(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Root:
                annotations:
                  xml_element: expected
                attributes:
                  known:
                    range: string
            """
        )
        with pytest.raises(XMLLoadErrors) as excinfo:
            xml_loader.load_as_dict(
                "<wrong><known>x</known><stray>y</stray></wrong>",
                target_class="Root",
                schemaview=sv,
                strict=True,
            )
        msgs = excinfo.value.errors
        # Two errors: root mismatch + stray element
        assert len(msgs) == 2
        assert any("wrong" in m and "expected" in m for m in msgs)
        assert any("stray" in m for m in msgs)


class TestStrictWithXmlPath:
    """xml_path intermediate elements shouldn't be flagged as unknown."""

    def test_strict_does_not_flag_xml_path_ancestors(self, make_schema):
        # When a slot uses xml_path: total/stats/stat/@min, the
        # direct child <total> is NOT in element_slots and would
        # otherwise be reported as unknown in strict mode. Verify the
        # path-aware exemption kicks in.
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  min:
                    range: string
                    annotations:
                      xml_path: total/stats/stat/@min
            """
        )
        xml = (
            "<variable>"
            "<total><stats><stat min=\"18\"/></stats></total>"
            "</variable>"
        )
        result = xml_loader.load_as_dict(
            xml, target_class="Variable", schemaview=sv, strict=True
        )
        assert result == {"min": "18"}


class TestXmlPathNamespaces:
    """xml_path should be namespace-agnostic, matching the loader's
    overall local-name contract."""

    def test_resolve_path_through_namespaced_elements(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  min:
                    range: string
                    annotations:
                      xml_path: total/stats/stat/@min
            """
        )
        xml = (
            '<variable xmlns:ns="http://example.org/ns">'
            '<ns:total><ns:stats><ns:stat min="18"/></ns:stats></ns:total>'
            "</variable>"
        )
        result = xml_loader.load_as_dict(
            xml, target_class="Variable", schemaview=sv
        )
        assert result == {"min": "18"}

    def test_resolve_path_with_namespaced_attribute(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Variable:
                attributes:
                  kind:
                    range: string
                    annotations:
                      xml_path: meta/@type
            """
        )
        xml = (
            '<variable xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<meta xsi:type="numeric"/>'
            "</variable>"
        )
        result = xml_loader.load_as_dict(
            xml, target_class="Variable", schemaview=sv
        )
        assert result == {"kind": "numeric"}


class TestSourceDetectionEdgeCases:
    """Source-type detection: inline content vs path, on edge inputs."""

    def test_long_inline_xml_does_not_check_filesystem(self, make_schema):
        # Pre-fix, long single-line XML would have triggered
        # Path(source).exists() which can raise on path-length limits.
        # Content-based detection avoids that path entirely.
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        # Construct >4 KB of inline XML on a single line.
        big = '<thing code="' + ("x" * 5000) + '"/>'
        result = xml_loader.load_as_dict(
            big, target_class="Thing", schemaview=sv
        )
        assert result["code"] == "x" * 5000

    def test_inline_xml_with_leading_whitespace(self, make_schema):
        sv = make_schema(
            """
            id: https://example.org/t
            name: t
            prefixes: {linkml: https://w3id.org/linkml/}
            imports: [linkml:types]
            classes:
              Thing:
                attributes:
                  code:
                    range: string
                    annotations:
                      xml_attribute: true
            """
        )
        # Leading whitespace before '<' should still be detected as inline.
        result = xml_loader.load_as_dict(
            '   \n  <thing code="42"/>',
            target_class="Thing",
            schemaview=sv,
        )
        assert result == {"code": "42"}
