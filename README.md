# pygedreader

A Python library for parsing GEDCOM 5.5.1 files, with full support for Ancestry.com exports.

## Why pygedreader?

Ancestry.com is the largest genealogy platform, but their GEDCOM exports don't strictly follow the spec. They include custom tags, non-standard date formats, and place data where the spec says it shouldn't go. pygedreader was built to handle these quirks so you don't lose valuable family history data.

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

## CLI Usage

### Show file statistics

```bash
pygedreader info family-tree.ged
```

Output:
```
File: family-tree.ged

Header:
  Source: Ancestry.com Family Trees
  GEDCOM: 5.5.1
  Charset: UTF-8

Records:
  Individuals: 253
  Families: 99
  Sources: 81
  Media Objects: 54

Events:
  Individuals with birth: 218
  MARR under INDI (Ancestry quirk): 55
  Custom events (_MILT, etc.): 2
```

### Export to JSON

```bash
# Output to stdout
pygedreader parse family-tree.ged

# Output to file
pygedreader parse family-tree.ged -o output.json

# Compact JSON (no indentation)
pygedreader parse family-tree.ged --indent 0 -o output.json
```

## Library Usage

```python
from pygedreader import parse_file

# Parse a GEDCOM file
gedcom = parse_file("family-tree.ged")

# Access individuals
for person in gedcom.individuals:
    print(f"{person.display_name}")

    if person.birth and person.birth.date:
        print(f"  Born: {person.birth.date.original}")

    # Ancestry's custom military events
    for event in person.custom_events:
        if event.tag == "_MILT":
            print(f"  Military: {event.date.original if event.date else 'unknown'}")

# Traverse family relationships (references auto-resolve)
person = gedcom.get_individual("@I123@")
for fam_link in person.spouse_families:
    family = fam_link.family
    for child in family.children:
        print(f"Child: {child.individual.display_name}")

# Access Ancestry's custom tags
for source in person.sources:
    if "_APID" in source.custom_tags:
        print(f"Ancestry ID: {source.custom_tags['_APID'][0]}")
```

## Data Model

All records are Pydantic models with full type hints:

- `Individual` - Person with names, events, family links
- `Family` - Spouses and children with marriage/divorce events
- `Source` - Bibliographic sources with citations
- `Repository` - Archives and libraries
- `MediaObject` - Photos and documents

Every model includes a `custom_tags` dict that captures non-standard `_` prefixed tags, so no Ancestry data is lost.

## Development

Clone the repo and install dependencies:

```bash
git clone https://github.com/creising/pygedreader.git
cd pygedreader
uv sync
```

Run the CLI locally:

```bash
uv run pygedreader info family-tree.ged
uv run pygedreader parse family-tree.ged -o output.json
```

Use the library in a Python script:

```bash
uv run python -c "
from pygedreader import parse_file
gedcom = parse_file('family-tree.ged')
print(gedcom.stats)
"
```

Run type checking and linting:

```bash
uv run mypy src tests
uv run ruff check .
uv run pytest
```

## License

MIT
