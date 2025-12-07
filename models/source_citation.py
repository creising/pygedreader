"""GEDCOM source citation models.

Represents inline source citations that appear within events, names, and other structures.

GEDCOM 5.5.1: SOURCE_CITATION
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SOURCE_CITATION
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .base import GedcomBaseModel, XRef

if TYPE_CHECKING:
    from .source import Source


class SourceData(GedcomBaseModel):
    """Data sub-structure within a source citation.

    GEDCOM 5.5.1: SOURCE_CITATION (DATA sub-record)

    Ancestry exports often include a WWW field with URLs to source records.

    Attributes:
        date: Date of the source data. GEDCOM tag: DATE
        text: Transcribed text from the source. GEDCOM tag: TEXT
        www: URL to the source (Ancestry extension). GEDCOM tag: WWW
    """

    date: Optional[str] = Field(
        None,
        description="Date of the source data. GEDCOM tag: DATE",
    )
    text: Optional[str] = Field(
        None,
        description="Transcribed text from the source. GEDCOM tag: TEXT",
    )
    www: Optional[str] = Field(
        None,
        description="URL to source (Ancestry extension). GEDCOM tag: WWW",
    )


class SourceCitation(GedcomBaseModel):
    """Inline source citation attached to events, names, or records.

    GEDCOM 5.5.1: SOURCE_CITATION
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SOURCE_CITATION

    Source citations appear throughout GEDCOM files, linking facts to
    their documentary sources. They reference a top-level SOUR record
    and provide specific location details (page numbers, URLs, etc.).

    Ancestry-specific custom tags commonly found in citations:
    - _APID: Ancestry Person/Record ID
    - _HPID: Husband Person ID (on marriage sources)
    - _WPID: Wife Person ID (on marriage sources)

    These are stored in the inherited custom_tags dict.

    Attributes:
        xref: Reference to a top-level SOUR record. GEDCOM tag: SOUR @XREF@
        source: Resolved Source object (populated after parsing, excluded from serialization).
        page: Specific location within the source. GEDCOM tag: PAGE
        data: Nested DATA structure with date, text, and URL.
        notes: Notes attached to this citation. GEDCOM tag: NOTE
        quality: Quality/reliability rating (0-3). GEDCOM tag: QUAY
    """

    xref: Optional[XRef] = Field(
        None,
        description="Reference to top-level SOUR record. GEDCOM tag: SOUR @XREF@",
    )
    source: Optional["Source"] = Field(
        None,
        exclude=True,
        description="Resolved Source object (populated after parsing).",
    )
    page: Optional[str] = Field(
        None,
        description="Specific location in source. GEDCOM tag: PAGE",
    )
    data: Optional[SourceData] = Field(
        None,
        description="Nested DATA structure. GEDCOM tag: DATA",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Notes on this citation. GEDCOM tag: NOTE",
    )
    quality: Optional[int] = Field(
        None,
        ge=0,
        le=3,
        description="Quality rating (0=unreliable to 3=direct evidence). GEDCOM tag: QUAY",
    )
