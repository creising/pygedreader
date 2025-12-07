# pygedreader

A Python library for parsing GEDCOM 5.5.1 files with full support for Ancestry.com exports.

## Project Structure

```
pygedreader/
  models/           # Pydantic data models
  parser/           # GEDCOM tokenizer and parser
  tests/            # Unit tests
  cli.py            # Command-line interface
  spec.md           # Project specification
  family-tree.ged   # Sample Ancestry export for testing
```

## Style Conventions

### Documentation

- **Class docstrings**: Google style, reference FamilySearch GEDCOM spec
- **Field docs**: Use `Field(description="...")` with GEDCOM tag name included

```python
class Individual(GedcomRecord):
    """Represents an individual person.

    GEDCOM 5.5.1: INDIVIDUAL_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#INDIVIDUAL_RECORD

    Attributes:
        first_name: Given/first name(s). GEDCOM tag: GIVN
        surname: Family name. GEDCOM tag: SURN
    """

    first_name: Optional[str] = Field(
        None,
        description="Given/first name(s). GEDCOM tag: GIVN"
    )
```

### Naming

- Use readable field names, not GEDCOM shorthand: `first_name` not `GIVN`
- Family links on Individual: `parent_families`, `spouse_families`
- Spouses on Family: `spouses: list[SpouseLink]` (gender-neutral)
- Always include the GEDCOM tag in field descriptions for traceability

### Custom Tags

All Ancestry `_` prefixed custom tags are stored in `custom_tags: dict[str, list[Any]]` on every model.

## Key Design Decisions

| Decision | Choice |
|----------|--------|
| References | Auto-resolve after parsing; store both `xref` string and resolved object |
| Dates | Lenient parsing - preserve original text, best-effort component extraction |
| MARR under INDI | Dedicated `Individual.marriages` field (Ancestry quirk) |
| Missing refs | Set resolved field to `None` if target doesn't exist |

## References

- [GEDCOM 5.5.1 Specification](https://gedcom.io/specifications/FamilySearchGEDCOMv7.html)
- [Ancestry GEDCOM Export Quirks](spec.md)

## Tools

- **uv**: Project/dependency management
- **mypy**: Type checking
- **ruff**: Formatting and linting
- **pydoc**: Documentation generation
