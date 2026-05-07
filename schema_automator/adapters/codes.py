"""Serialization between the canonical structured `codes` form and the TSV
grammar (`code, label | code, label | ...`).

The canonical form (used in YAML and as the linkml-map operating
representation) is a list of dicts: each dict has at minimum a `code` key
and optionally a `label`. The TSV form is a single string with the
documented grammar:

  - tokens separated by `|`
  - each token is either a bareword (no comma) or `code, label`
  - the first comma in a token separates code from label; subsequent
    commas in the label are literal text
  - whitespace around the `|` separator is trimmed
  - `\\,`, `\\|`, `\\\\` are escapes for literal comma, pipe, backslash

Used by every adapter as the parse/serialize bookend, and by canonical
TSV ↔ YAML conversion.
"""

from __future__ import annotations


def _split_unescaped(s: str, delim: str) -> list[str]:
    """Split *s* on unescaped *delim*; ``\\delim`` is treated as literal."""
    out: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            cur.append(c)
            cur.append(s[i + 1])
            i += 2
            continue
        if c == delim:
            out.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur))
    return out


def _unescape(s: str) -> str:
    """Decode ``\\,``, ``\\|``, ``\\\\`` back to literal characters."""
    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] in "\\|,":
            out.append(s[i + 1])
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _escape_code(s: str) -> str:
    """Escape special characters in a code position.

    Codes cannot contain unescaped ``,`` (would be parsed as the
    code/label separator) or ``|`` (token separator). Backslash itself
    must be escaped to disambiguate from escape sequences.
    """
    return s.replace("\\", "\\\\").replace("|", "\\|").replace(",", "\\,")


def _escape_label(s: str) -> str:
    """Escape special characters in a label position.

    Labels can contain unescaped ``,`` — only the first comma in a token
    is parsed as the code/label separator. Backslash and pipe still need
    escaping.
    """
    return s.replace("\\", "\\\\").replace("|", "\\|")


def parse_codes(s: str) -> list[dict[str, str]]:
    """Parse the TSV codes grammar into a list of structured records.

    Each output record has a ``code`` key and optionally a ``label`` key.
    Records without a label correspond to bareword tokens (the literal
    data value is its own meaning).

    Empty input yields an empty list. Empty tokens raise ``ValueError``.
    """
    if not s or not s.strip():
        return []
    out: list[dict[str, str]] = []
    for raw_token in _split_unescaped(s, "|"):
        token = raw_token.strip()
        if not token:
            raise ValueError(f"Empty token in codes string: {s!r}")
        parts = _split_unescaped(token, ",")
        if len(parts) == 1:
            out.append({"code": _unescape(parts[0].strip())})
        else:
            code = _unescape(parts[0].strip())
            # Rejoin everything after the first comma; labels may contain
            # unescaped commas as literal text.
            label_raw = ",".join(parts[1:]).lstrip()
            out.append({"code": code, "label": _unescape(label_raw)})
    return out


def serialize_codes(codes: list[dict[str, str]]) -> str:
    """Serialize a list of structured code records to the TSV grammar.

    A record with a ``label`` produces a ``code, label`` token; a record
    without a ``label`` (or with an empty label) produces a bareword
    token. The output uses ``" | "`` (space-pipe-space) as the token
    separator to match the prose spec's example formatting.

    The result round-trips through ``parse_codes`` modulo whitespace
    normalization.
    """
    if not codes:
        return ""
    tokens: list[str] = []
    for entry in codes:
        if "code" not in entry:
            raise ValueError(f"Code record missing 'code' key: {entry!r}")
        code = _escape_code(entry["code"])
        label = entry.get("label")
        if label is None or label == "":
            tokens.append(code)
        else:
            tokens.append(f"{code}, {_escape_label(label)}")
    return " | ".join(tokens)
