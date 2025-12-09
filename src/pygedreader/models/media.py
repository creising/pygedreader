"""GEDCOM media object model.

Represents multimedia objects (photos, documents, etc.).

GEDCOM 5.5.1: MULTIMEDIA_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#MULTIMEDIA_RECORD
"""

from __future__ import annotations

from pydantic import Field

from .base import GedcomBaseModel, GedcomRecord
from .date import GedcomDate
from .place import Place


class MediaFile(GedcomBaseModel):
    """File information within a media object.

    GEDCOM 5.5.1: MULTIMEDIA_RECORD (FILE sub-record)

    Ancestry exports include extensive custom metadata about files:
    _MTYPE, _STYPE, _SIZE, _WDTH, _HGHT (stored in custom_tags).

    Attributes:
        path: File path or reference. GEDCOM tag: FILE
        format: File format (jpg, png, pdf, etc.). GEDCOM tag: FORM
        media_type: General media type (image, video, etc.). GEDCOM tag: TYPE
        title: Title of the media. GEDCOM tag: TITL
    """

    path: str | None = Field(
        None,
        description="File path or reference. GEDCOM tag: FILE",
    )
    format: str | None = Field(
        None,
        description="File format (jpg, png, pdf). GEDCOM tag: FORM",
    )
    media_type: str | None = Field(
        None,
        description="General media type (image, video). GEDCOM tag: TYPE",
    )
    title: str | None = Field(
        None,
        description="Title of the media. GEDCOM tag: TITL",
    )


class MediaObject(GedcomRecord):
    """Represents a multimedia object (photo, document, etc.).

    GEDCOM 5.5.1: MULTIMEDIA_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#MULTIMEDIA_RECORD

    Media objects are referenced from individuals, families, and other records.
    Ancestry exports include extensive custom metadata:

    - _OID: Ancestry object ID
    - _META: XML metadata
    - _CREA: Creation timestamp
    - _USER: User reference (encrypted)
    - _CLON: Cloning information
    - _ORIG: Origin information
    - _ATL: Atlas flag
    - _PRIM: Primary media flag

    These are stored in the inherited custom_tags dict.

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @O123@
        file: File information. GEDCOM tag: FILE
        date: Date of media subject. GEDCOM tag: DATE
        place: Place depicted in media. GEDCOM tag: PLAC
    """

    file: MediaFile | None = Field(
        None,
        description="File information. GEDCOM tag: FILE",
    )
    date: GedcomDate | None = Field(
        None,
        description="Date of media subject. GEDCOM tag: DATE",
    )
    place: Place | None = Field(
        None,
        description="Place depicted in media. GEDCOM tag: PLAC",
    )
