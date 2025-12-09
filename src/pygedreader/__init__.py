"""pygedreader - A Python library for parsing GEDCOM files.

Supports GEDCOM 5.5.1 with full Ancestry.com export compatibility.

Example usage:
    from pygedreader import parse_file

    gedcom = parse_file("family-tree.ged")
    for person in gedcom.individuals:
        print(person.display_name)
"""

from pygedreader.parser import parse_file, parse_fileobj, parse_string

__version__ = "0.1.0"
__all__ = [
    "parse_file",
    "parse_fileobj",
    "parse_string",
]
