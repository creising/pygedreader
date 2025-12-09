"""GEDCOM line tokenizer.

Parses individual lines of a GEDCOM file into structured tokens.

GEDCOM line format:
    LEVEL [XREF] TAG [VALUE]

Examples:
    0 HEAD
    0 @I123@ INDI
    1 NAME John /Smith/
    2 GIVN John
    2 SOUR @S456@
    3 PAGE Page 123
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TextIO

# Regex pattern for parsing GEDCOM lines
# Format: LEVEL [XREF] TAG [VALUE]
LINE_PATTERN = re.compile(
    r"^(?P<level>\d+)"  # Level number
    r"\s+"
    r"(?:(?P<xref>@[^@]+@)\s+)?"  # Optional XREF
    r"(?P<tag>[A-Za-z0-9_]+)"  # Tag
    r"(?:\s+(?P<value>.*))?$"  # Optional value
)


@dataclass(frozen=True, slots=True)
class GedcomLine:
    """Represents a single parsed GEDCOM line.

    Attributes:
        level: Hierarchical level (0 for top-level records).
        tag: GEDCOM tag (INDI, NAME, BIRT, etc.).
        value: Optional value after the tag.
        xref: Optional cross-reference identifier (@I123@).
        line_number: Original line number in the file (1-based).
    """

    level: int
    tag: str
    value: str | None
    xref: str | None
    line_number: int

    @property
    def is_record_start(self) -> bool:
        """Check if this line starts a new top-level record."""
        return self.level == 0 and self.xref is not None

    @property
    def is_custom_tag(self) -> bool:
        """Check if this is a custom (underscore-prefixed) tag."""
        return self.tag.startswith("_")


def tokenize_line(line: str, line_number: int) -> GedcomLine | None:
    """Parse a single GEDCOM line into a GedcomLine token.

    Args:
        line: Raw line from GEDCOM file.
        line_number: Line number for error reporting (1-based).

    Returns:
        GedcomLine if parsing succeeds, None for empty/invalid lines.
    """
    line = line.rstrip("\r\n")

    # Skip empty lines
    if not line.strip():
        return None

    # Handle BOM at start of file
    if line.startswith("\ufeff"):
        line = line[1:]

    match = LINE_PATTERN.match(line)
    if not match:
        # Could log a warning here for malformed lines
        return None

    level = int(match.group("level"))
    xref = match.group("xref")
    tag = match.group("tag").upper()  # Normalize to uppercase
    value = match.group("value")

    # Strip whitespace from value but preserve None vs empty
    if value is not None:
        value = value.strip()
        if not value:
            value = None

    return GedcomLine(
        level=level,
        tag=tag,
        value=value,
        xref=xref,
        line_number=line_number,
    )


def tokenize_file(file: TextIO) -> Iterator[GedcomLine]:
    """Tokenize an entire GEDCOM file.

    Args:
        file: Open file handle to read from.

    Yields:
        GedcomLine tokens for each valid line.
    """
    for line_number, line in enumerate(file, start=1):
        token = tokenize_line(line, line_number)
        if token is not None:
            yield token


def tokenize_string(content: str) -> Iterator[GedcomLine]:
    """Tokenize GEDCOM content from a string.

    Args:
        content: GEDCOM file content as a string.

    Yields:
        GedcomLine tokens for each valid line.
    """
    for line_number, line in enumerate(content.splitlines(), start=1):
        token = tokenize_line(line, line_number)
        if token is not None:
            yield token
