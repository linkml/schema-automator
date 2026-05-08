"""Tests for the codes serialization utility."""

import pytest

from schema_automator.adapters.codes import parse_codes, serialize_codes


class TestParseCodes:
    def test_empty(self):
        assert parse_codes("") == []
        assert parse_codes("   ") == []

    def test_single_code_label(self):
        assert parse_codes("1, Yes") == [{"code": "1", "label": "Yes"}]

    def test_multiple_code_label(self):
        assert parse_codes("1, Yes | 0, No | 2, Unknown") == [
            {"code": "1", "label": "Yes"},
            {"code": "0", "label": "No"},
            {"code": "2", "label": "Unknown"},
        ]

    def test_bareword(self):
        assert parse_codes("EHR | Survey | Lab") == [
            {"code": "EHR"},
            {"code": "Survey"},
            {"code": "Lab"},
        ]

    def test_mixed_bareword_and_pair(self):
        assert parse_codes("EHR | 1, Yes") == [
            {"code": "EHR"},
            {"code": "1", "label": "Yes"},
        ]

    def test_label_with_unescaped_comma(self):
        # Spec: only the first comma in a token is the separator;
        # subsequent commas in the label are literal text.
        assert parse_codes("1, Female, age 65+") == [
            {"code": "1", "label": "Female, age 65+"},
        ]

    def test_escaped_comma_in_code(self):
        # A code containing a literal comma must escape it.
        assert parse_codes(r">=$50\,000, Middle income") == [
            {"code": ">=$50,000", "label": "Middle income"},
        ]

    def test_escaped_pipe(self):
        assert parse_codes(r"a\|b, contains pipe") == [
            {"code": "a|b", "label": "contains pipe"},
        ]

    def test_escaped_backslash(self):
        assert parse_codes(r"a\\b, contains backslash") == [
            {"code": "a\\b", "label": "contains backslash"},
        ]

    def test_escaped_comma_in_label(self):
        # Labels may contain unescaped commas, but escaped commas should
        # also decode correctly.
        assert parse_codes(r"1, Black\, non-Hispanic") == [
            {"code": "1", "label": "Black, non-Hispanic"},
        ]

    def test_whitespace_around_pipe(self):
        # Whitespace around the pipe separator is trimmed.
        assert parse_codes("a|b") == [{"code": "a"}, {"code": "b"}]
        assert parse_codes("a    |    b") == [{"code": "a"}, {"code": "b"}]

    def test_empty_token_rejected(self):
        with pytest.raises(ValueError, match="Empty token"):
            parse_codes("a | | b")


class TestSerializeCodes:
    def test_empty(self):
        assert serialize_codes([]) == ""

    def test_single_code_label(self):
        assert serialize_codes([{"code": "1", "label": "Yes"}]) == "1, Yes"

    def test_multiple(self):
        assert serialize_codes([
            {"code": "1", "label": "Yes"},
            {"code": "0", "label": "No"},
        ]) == "1, Yes | 0, No"

    def test_bareword(self):
        assert serialize_codes([{"code": "EHR"}, {"code": "Survey"}]) == "EHR | Survey"

    def test_empty_label_treated_as_bareword(self):
        # An entry with label="" should serialize as bareword, not "code, ".
        assert serialize_codes([{"code": "EHR", "label": ""}]) == "EHR"

    def test_escapes_comma_in_code(self):
        assert serialize_codes([
            {"code": ">=$50,000", "label": "Middle income"},
        ]) == r">=$50\,000, Middle income"

    def test_escapes_pipe_in_code_and_label(self):
        assert serialize_codes([
            {"code": "a|b", "label": "has|pipe"},
        ]) == r"a\|b, has\|pipe"

    def test_escapes_backslash(self):
        assert serialize_codes([
            {"code": "a\\b", "label": "c\\d"},
        ]) == r"a\\b, c\\d"

    def test_label_comma_not_escaped(self):
        # Labels can contain unescaped commas; serializer should not
        # gratuitously escape them.
        assert serialize_codes([
            {"code": "1", "label": "Female, age 65+"},
        ]) == "1, Female, age 65+"

    def test_missing_code_rejected(self):
        with pytest.raises(ValueError, match="missing 'code'"):
            serialize_codes([{"label": "no code key"}])


class TestRoundTrip:
    """parse(serialize(x)) == x for representative inputs."""

    @pytest.mark.parametrize(
        "codes",
        [
            [],
            [{"code": "1", "label": "Yes"}],
            [
                {"code": "1", "label": "Yes"},
                {"code": "0", "label": "No"},
                {"code": "2", "label": "Unknown"},
            ],
            [{"code": "EHR"}, {"code": "Survey"}, {"code": "Lab"}],
            [
                {"code": "1", "label": "Female, age 65+"},
                {"code": "2", "label": "Male, age 65+"},
            ],
            [
                {"code": ">=$50,000", "label": "Middle income"},
                {"code": "<$50,000", "label": "Low income"},
            ],
            [{"code": "a|b", "label": "has|pipe"}],
            [{"code": "a\\b", "label": "c\\d"}],
        ],
    )
    def test_roundtrip(self, codes):
        assert parse_codes(serialize_codes(codes)) == codes
