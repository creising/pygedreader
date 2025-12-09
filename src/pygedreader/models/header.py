"""GEDCOM header model.

Represents the file header containing metadata about the GEDCOM file.

GEDCOM 5.5.1: HEADER
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#HEADER
"""

from __future__ import annotations

from pydantic import Field

from .base import GedcomBaseModel, XRef
from .date import GedcomDate


class GedcomVersion(GedcomBaseModel):
    """GEDCOM version information.

    GEDCOM 5.5.1: HEADER (GEDC sub-record)

    Attributes:
        version: GEDCOM version number (e.g., "5.5.1"). GEDCOM tag: VERS
        form: GEDCOM form (typically "LINEAGE-LINKED"). GEDCOM tag: FORM
    """

    version: str = Field(
        ...,
        description="GEDCOM version (e.g., '5.5.1'). GEDCOM tag: VERS",
    )
    form: str = Field(
        "LINEAGE-LINKED",
        description="GEDCOM form. GEDCOM tag: FORM",
    )


class SourceSystem(GedcomBaseModel):
    """Information about the system that generated the GEDCOM file.

    GEDCOM 5.5.1: HEADER (SOUR sub-record)

    Ancestry-specific: The _TREE custom tag contains the tree name,
    stored in custom_tags.

    Attributes:
        system_id: Source system identifier. GEDCOM tag: SOUR
        name: System name. GEDCOM tag: NAME
        version: System version. GEDCOM tag: VERS
        corporation: Corporation name. GEDCOM tag: CORP
        phone: Corporation phone. GEDCOM tag: PHON (under CORP)
        website: Corporation website. GEDCOM tag: WWW (under CORP)
        address: Corporation address. GEDCOM tag: ADDR (under CORP)
    """

    system_id: str = Field(
        ...,
        description="Source system identifier. GEDCOM tag: SOUR",
    )
    name: str | None = Field(
        None,
        description="System name. GEDCOM tag: NAME",
    )
    version: str | None = Field(
        None,
        description="System version. GEDCOM tag: VERS",
    )
    corporation: str | None = Field(
        None,
        description="Corporation name. GEDCOM tag: CORP",
    )
    phone: str | None = Field(
        None,
        description="Corporation phone. GEDCOM tag: PHON",
    )
    website: str | None = Field(
        None,
        description="Corporation website. GEDCOM tag: WWW",
    )
    address: str | None = Field(
        None,
        description="Corporation address. GEDCOM tag: ADDR",
    )


class Header(GedcomBaseModel):
    """Represents the GEDCOM file header.

    GEDCOM 5.5.1: HEADER
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#HEADER

    The header contains metadata about the GEDCOM file including
    the source system, export date, GEDCOM version, and character encoding.

    Attributes:
        source: Source system information. GEDCOM tag: SOUR
        date: Export date. GEDCOM tag: DATE
        time: Export time. GEDCOM tag: TIME
        submitter_xref: Reference to submitter record. GEDCOM tag: SUBM
        gedcom_version: GEDCOM version info. GEDCOM tag: GEDC
        charset: Character encoding. GEDCOM tag: CHAR
        language: Language. GEDCOM tag: LANG
        filename: Original filename. GEDCOM tag: FILE
        notes: Header notes. GEDCOM tag: NOTE
    """

    source: SourceSystem | None = Field(
        None,
        description="Source system information. GEDCOM tag: SOUR",
    )
    date: GedcomDate | None = Field(
        None,
        description="Export date. GEDCOM tag: DATE",
    )
    time: str | None = Field(
        None,
        description="Export time. GEDCOM tag: TIME",
    )
    submitter_xref: XRef | None = Field(
        None,
        description="Reference to submitter. GEDCOM tag: SUBM",
    )
    gedcom_version: GedcomVersion | None = Field(
        None,
        description="GEDCOM version info. GEDCOM tag: GEDC",
    )
    charset: str = Field(
        "UTF-8",
        description="Character encoding. GEDCOM tag: CHAR",
    )
    language: str | None = Field(
        None,
        description="Language. GEDCOM tag: LANG",
    )
    filename: str | None = Field(
        None,
        description="Original filename. GEDCOM tag: FILE",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Header notes. GEDCOM tag: NOTE",
    )
