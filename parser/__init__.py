"""GEDCOM parser package.

Provides functionality to parse GEDCOM files into Pydantic models.

Example usage:
    from parser import parse_file

    gedcom = parse_file("family-tree.ged")
    print(f"Loaded {len(gedcom.individuals)} individuals")

    for person in gedcom.individuals:
        print(person.display_name)
"""

from .parser import parse_file, parse_fileobj, parse_string
from .tokenizer import GedcomLine, tokenize_file, tokenize_line, tokenize_string
from .tree import GedcomNode, build_tree, group_by_record_type

__all__ = [
    # Main parser functions
    "parse_file",
    "parse_fileobj",
    "parse_string",
    # Tokenizer
    "GedcomLine",
    "tokenize_file",
    "tokenize_line",
    "tokenize_string",
    # Tree builder
    "GedcomNode",
    "build_tree",
    "group_by_record_type",
]
