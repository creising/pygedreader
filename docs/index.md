# pygedreader

A Python library for parsing GEDCOM 5.5.1 files with full support for Ancestry.com exports.

## Why pygedreader?

Ancestry.com is the largest genealogy platform, but their GEDCOM exports don't strictly follow the spec. They include custom tags, non-standard date formats, and place data where the spec says it shouldn't go. pygedreader handles these quirks so you don't lose valuable family history data.

**What we handle:**

- **MARR events under INDI records** - Ancestry puts marriage data on individuals, not just families
- **Custom `_` tags** - Preserves `_APID` (Ancestry IDs), `_MILT` (military service), `_OID` (media IDs), and 30+ other extensions
- **Inline notes with structured data** - Parses "Occupation: Farmer; Marital Status: Married" into key-value pairs
- **Non-standard date formats** - Handles year ranges like "2010-2019" and slash dates like "05/28/1960"

## Installation

```bash
pip install pygedreader
```

Or with uv:

```bash
uv add pygedreader
```

## Quick Example

```python
from pygedreader import parse_file

gedcom = parse_file("family-tree.ged")

for person in gedcom.individuals:
    print(person.display_name)

    if person.birth and person.birth.date:
        print(f"  Born: {person.birth.date.original}")
```

## Features

- **Typed models** - All records are Pydantic models with full type hints
- **Auto-resolved references** - Cross-references between individuals, families, and sources resolve automatically
- **CLI tool** - Quick file inspection and JSON export
- **Ancestry compatible** - Handles all known Ancestry.com GEDCOM quirks

## Next Steps

- [Getting Started](getting-started.md) - Full tutorial
- [CLI Reference](cli.md) - Command-line usage
- [API Reference](api/index.md) - Full API documentation
