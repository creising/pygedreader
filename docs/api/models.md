# Models

All GEDCOM records are represented as Pydantic models with full type hints.

## Root Container

### Gedcom

::: pygedreader.models.Gedcom
    options:
      members:
        - header
        - individuals
        - families
        - sources
        - repositories
        - media_objects
        - get_individual
        - get_family
        - get_source
        - stats

## Records

### Individual

::: pygedreader.models.Individual
    options:
      members:
        - xref
        - names
        - primary_name
        - display_name
        - sex
        - birth
        - death
        - events
        - custom_events
        - parent_families
        - spouse_families
        - sources

### Family

::: pygedreader.models.Family
    options:
      members:
        - xref
        - spouses
        - children
        - marriage
        - divorce

### Source

::: pygedreader.models.Source
    options:
      members:
        - xref
        - title
        - author
        - publication

## Supporting Models

### Name

::: pygedreader.models.Name
    options:
      members:
        - full
        - first_name
        - surname
        - prefix
        - suffix
        - nickname

### Event

::: pygedreader.models.Event
    options:
      members:
        - tag
        - event_type
        - date
        - place
        - sources

### GedcomDate

::: pygedreader.models.GedcomDate
    options:
      members:
        - original
        - year
        - month
        - day
        - modifier
        - date_value

### Place

::: pygedreader.models.Place
    options:
      members:
        - name
        - city
        - county
        - state
        - country
        - latitude
        - longitude

## Link Models

These models represent references between records:

### FamilyLink

::: pygedreader.models.FamilyLink

### SpouseLink

::: pygedreader.models.SpouseLink

### ChildLink

::: pygedreader.models.ChildLink

### SourceCitation

::: pygedreader.models.SourceCitation
