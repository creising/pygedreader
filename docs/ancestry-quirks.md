# Ancestry.com GEDCOM Quirks

Ancestry.com exports GEDCOM files with several non-standard features. pygedreader handles all of these automatically.

## Custom Tags

Ancestry uses many `_` prefixed custom tags that aren't part of the GEDCOM standard. All custom tags are preserved in the `custom_tags` dictionary on each model.

### Common Custom Tags

| Tag | Description | Found On |
|-----|-------------|----------|
| `_APID` | Ancestry Person/Record ID | Sources, citations |
| `_MILT` | Military service event | Individuals |
| `_OID` | Object ID for media | Media objects |
| `_TREE` | Family tree name | Header |
| `_MTYPE` | Media type | Media files |
| `_SIZE` | File size | Media files |
| `_WDTH` | Image width | Media files |
| `_HGHT` | Image height | Media files |

### Accessing Custom Tags

```python
person = gedcom.get_individual("@I123@")

# Check for custom tag
if "_APID" in person.custom_tags:
    ancestry_id = person.custom_tags["_APID"][0]
    print(f"Ancestry ID: {ancestry_id}")

# Custom events (like _MILT)
for event in person.custom_events:
    if event.tag == "_MILT":
        print(f"Military: {event.date.original if event.date else 'unknown'}")
```

## MARR Under INDI

Standard GEDCOM places marriage events (MARR) only under FAM records. Ancestry also puts them under INDI records, storing marriage information directly on individuals.

pygedreader captures these in `individual.marriages`:

```python
person = gedcom.get_individual("@I123@")

# Ancestry-style marriages on individual
for marriage in person.marriages:
    print(f"Marriage date: {marriage.date.original if marriage.date else 'unknown'}")
    print(f"Marriage place: {marriage.place.name if marriage.place else 'unknown'}")
```

## Non-Standard Date Formats

Ancestry exports dates in formats not covered by the GEDCOM spec:

### Year Ranges

```
DATE 2010-2019
```

Parsed as a range with `year=2010` and `year_end=2019`.

### Slash Dates

```
DATE 05/28/1960
```

Parsed as month=5, day=28, year=1960.

### Handling Dates

```python
date = person.birth.date

# Original text is always preserved
print(date.original)  # "2010-2019" or "05/28/1960"

# Components extracted when possible
if date.year_end:
    print(f"Range: {date.year} to {date.year_end}")
else:
    print(f"Year: {date.year}")
```

## SEX with Sources

Ancestry attaches source citations to SEX tags, which is unusual:

```
1 SEX M
2 SOUR @S123@
```

These sources are captured in `individual.sex_sources`:

```python
person = gedcom.get_individual("@I123@")

for citation in person.sex_sources:
    print(f"Sex sourced from: {citation.source.title}")
```

## Media Object Extensions

Ancestry includes detailed metadata on media files:

```
0 @O1@ OBJE
1 FILE
2 FORM jpg
3 TYPE image
3 _MTYPE document
3 _SIZE 196382
3 _WDTH 2070
3 _HGHT 1730
```

Access via the `MediaFile` model:

```python
media = gedcom.get_media("@O1@")

if media.file:
    print(f"Format: {media.file.format}")
    print(f"Size: {media.file.custom_tags.get('_SIZE', ['unknown'])[0]} bytes")
```

## Notes with Structured Data

Ancestry sometimes embeds structured data in notes:

```
1 NOTE Occupation: Farmer; Marital Status: Married
```

pygedreader parses these into key-value pairs:

```python
for note in person.notes:
    if note.structured_data:
        for key, value in note.structured_data.items():
            print(f"{key}: {value}")
```
