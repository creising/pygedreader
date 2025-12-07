"""GEDCOM source record model.

Represents bibliographic sources referenced by citations throughout the file.

GEDCOM 5.5.1: SOURCE_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SOURCE_RECORD
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .base import GedcomBaseModel, GedcomRecord, XRef
from .date import GedcomDate
from .note import Note
from .place import Place

if TYPE_CHECKING:
    from .repository import Repository


class SourcePublication(GedcomBaseModel):
    """Publication details for a source.

    GEDCOM 5.5.1: SOURCE_RECORD (PUBL sub-record)

    Attributes:
        text: Publisher or publication information. GEDCOM tag: PUBL
        date: Publication date. GEDCOM tag: DATE (under PUBL)
        place: Publication place. GEDCOM tag: PLAC (under PUBL)
    """

    text: str = Field(
        ...,
        description="Publisher/publication text. GEDCOM tag: PUBL",
    )
    date: Optional[GedcomDate] = Field(
        None,
        description="Publication date. GEDCOM tag: DATE",
    )
    place: Optional[Place] = Field(
        None,
        description="Publication place. GEDCOM tag: PLAC",
    )


class Source(GedcomRecord):
    """Represents a bibliographic source.

    GEDCOM 5.5.1: SOURCE_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SOURCE_RECORD

    Sources are top-level records referenced by SourceCitation objects
    throughout the GEDCOM file. They contain bibliographic information
    about documents, books, websites, etc.

    Ancestry-specific: The _APID custom tag contains Ancestry's internal
    database ID for the source, stored in custom_tags.

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @S123@
        title: Source title. GEDCOM tag: TITL
        author: Author name(s). GEDCOM tag: AUTH
        abbreviation: Short title or abbreviation. GEDCOM tag: ABBR
        publication: Publication details. GEDCOM tag: PUBL
        repository_xref: Reference to repository. GEDCOM tag: REPO
        repository: Resolved Repository object (populated after parsing).
        notes: Notes about this source. GEDCOM tag: NOTE
    """

    title: Optional[str] = Field(
        None,
        description="Source title. GEDCOM tag: TITL",
    )
    author: Optional[str] = Field(
        None,
        description="Author name(s). GEDCOM tag: AUTH",
    )
    abbreviation: Optional[str] = Field(
        None,
        description="Short title or abbreviation. GEDCOM tag: ABBR",
    )
    publication: Optional[SourcePublication] = Field(
        None,
        description="Publication details. GEDCOM tag: PUBL",
    )
    repository_xref: Optional[XRef] = Field(
        None,
        description="Reference to repository. GEDCOM tag: REPO",
    )
    repository: Optional["Repository"] = Field(
        None,
        exclude=True,
        description="Resolved Repository object (populated after parsing).",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="Notes about this source. GEDCOM tag: NOTE",
    )
