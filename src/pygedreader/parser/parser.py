"""Main GEDCOM parser.

Parses a complete GEDCOM file into a Gedcom model object.
"""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from pygedreader.models import Gedcom

from .record_parser import (
    parse_family,
    parse_header,
    parse_individual,
    parse_media_object,
    parse_repository,
    parse_source,
    parse_submitter,
)
from .tokenizer import tokenize_file, tokenize_string
from .tree import GedcomNode, build_tree, group_by_record_type


def parse_file(path: str | Path, encoding: str = "utf-8") -> Gedcom:
    """Parse a GEDCOM file into a Gedcom model.

    Args:
        path: Path to the GEDCOM file.
        encoding: File encoding (default: utf-8).

    Returns:
        Parsed Gedcom object with all records and resolved references.
    """
    path = Path(path)
    with open(path, encoding=encoding) as f:
        return parse_fileobj(f)


def parse_string(content: str) -> Gedcom:
    """Parse GEDCOM content from a string.

    Args:
        content: GEDCOM file content as a string.

    Returns:
        Parsed Gedcom object with all records and resolved references.
    """
    tokens = tokenize_string(content)
    nodes = build_tree(tokens)
    return _parse_nodes(nodes)


def parse_fileobj(file: TextIO) -> Gedcom:
    """Parse GEDCOM content from a file object.

    Args:
        file: Open file handle to read from.

    Returns:
        Parsed Gedcom object with all records and resolved references.
    """
    tokens = tokenize_file(file)
    nodes = build_tree(tokens)
    return _parse_nodes(nodes)


def _parse_nodes(nodes: list[GedcomNode]) -> Gedcom:
    """Parse tree nodes into a Gedcom model.

    Args:
        nodes: List of top-level GedcomNode objects.

    Returns:
        Parsed Gedcom object with all records and resolved references.
    """
    groups = group_by_record_type(nodes)

    gedcom = Gedcom()

    # Parse header
    head_nodes = groups.get("HEAD", [])
    if head_nodes:
        gedcom.header = parse_header(head_nodes[0])

    # Parse submitters
    for node in groups.get("SUBM", []):
        try:
            gedcom.submitters.append(parse_submitter(node))
        except ValueError:
            # Skip malformed records
            pass

    # Parse individuals
    for node in groups.get("INDI", []):
        try:
            gedcom.individuals.append(parse_individual(node))
        except ValueError:
            pass

    # Parse families
    for node in groups.get("FAM", []):
        try:
            gedcom.families.append(parse_family(node))
        except ValueError:
            pass

    # Parse sources
    for node in groups.get("SOUR", []):
        try:
            gedcom.sources.append(parse_source(node))
        except ValueError:
            pass

    # Parse repositories
    for node in groups.get("REPO", []):
        try:
            gedcom.repositories.append(parse_repository(node))
        except ValueError:
            pass

    # Parse media objects
    for node in groups.get("OBJE", []):
        try:
            gedcom.media_objects.append(parse_media_object(node))
        except ValueError:
            pass

    # Resolve all cross-references
    gedcom.resolve_references()

    return gedcom
