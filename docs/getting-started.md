# Getting Started

This guide walks through parsing a GEDCOM file and accessing the data.

## Basic Usage

```python
from pygedreader import parse_file

# Parse a GEDCOM file
gedcom = parse_file("family-tree.ged")

# See what's in the file
print(gedcom.stats)
# {'individuals': 253, 'families': 99, 'sources': 81, ...}
```

## Accessing Individuals

```python
# Iterate all individuals
for person in gedcom.individuals:
    print(person.display_name)

# Look up by XREF
person = gedcom.get_individual("@I123@")
```

## Working with Names

Individuals can have multiple names (birth name, married name, aliases):

```python
person = gedcom.get_individual("@I123@")

# Primary name (first in list)
print(person.primary_name.first_name)  # "John"
print(person.primary_name.surname)     # "Smith"

# All names
for name in person.names:
    print(f"{name.full} ({name.name_type or 'primary'})")
```

## Events and Dates

```python
person = gedcom.get_individual("@I123@")

# Birth event
if person.birth:
    print(f"Born: {person.birth.date.original}")
    print(f"Place: {person.birth.place.name}")

# Death event
if person.death:
    print(f"Died: {person.death.date.original}")

# All events (residence, occupation, etc.)
for event in person.events:
    print(f"{event.tag}: {event.date.original if event.date else 'unknown'}")
```

### Date Components

Dates are parsed into components when possible:

```python
date = person.birth.date

print(date.original)  # "4 Jun 1982"
print(date.year)      # 1982
print(date.month)     # 6
print(date.day)       # 4
print(date.date_value)  # datetime.date(1982, 6, 4)

# Date modifiers
print(date.modifier)  # DateModifier.ABOUT, DateModifier.BEFORE, etc.
```

## Family Relationships

References between records are automatically resolved:

```python
person = gedcom.get_individual("@I123@")

# Families where this person is a spouse
for fam_link in person.spouse_families:
    family = fam_link.family

    # Other spouse
    for spouse in family.spouses:
        if spouse.xref != person.xref:
            print(f"Married to: {spouse.individual.display_name}")

    # Children
    for child in family.children:
        print(f"Child: {child.individual.display_name}")

# Families where this person is a child
for fam_link in person.parent_families:
    family = fam_link.family
    print(f"Parents' family: {family.xref}")
```

## Sources and Citations

```python
person = gedcom.get_individual("@I123@")

# Sources attached to the individual
for citation in person.sources:
    if citation.source:
        print(f"Source: {citation.source.title}")
    print(f"Page: {citation.page}")

# Sources on specific events
if person.birth:
    for citation in person.birth.sources:
        print(f"Birth source: {citation.source.title}")
```

## Custom Tags (Ancestry)

Non-standard tags are preserved in `custom_tags`:

```python
person = gedcom.get_individual("@I123@")

# Ancestry Person ID
if "_APID" in person.custom_tags:
    print(f"Ancestry ID: {person.custom_tags['_APID'][0]}")

# Custom events (military service, etc.)
for event in person.custom_events:
    print(f"{event.tag}: {event.date.original if event.date else ''}")
```

## Parsing from String

```python
from pygedreader import parse_string

gedcom_content = """
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
0 TRLR
"""

gedcom = parse_string(gedcom_content)
```
