"""GEDCOM submitter model.

Represents the person or organization that submitted the GEDCOM file.

GEDCOM 5.5.1: SUBMITTER_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SUBMITTER_RECORD
"""

from __future__ import annotations

from pydantic import Field

from .base import GedcomRecord


class Submitter(GedcomRecord):
    """Represents the file submitter.

    GEDCOM 5.5.1: SUBMITTER_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#SUBMITTER_RECORD

    The submitter is referenced from the file header and identifies
    who created or submitted the GEDCOM file.

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @SUBM1@
        name: Submitter name. GEDCOM tag: NAME
        address: Postal address. GEDCOM tag: ADDR
        phone: Phone number. GEDCOM tag: PHON
        email: Email address. GEDCOM tag: EMAIL
        website: Website URL. GEDCOM tag: WWW
    """

    name: str = Field(
        ...,
        description="Submitter name. GEDCOM tag: NAME",
    )
    address: str | None = Field(
        None,
        description="Postal address. GEDCOM tag: ADDR",
    )
    phone: str | None = Field(
        None,
        description="Phone number. GEDCOM tag: PHON",
    )
    email: str | None = Field(
        None,
        description="Email address. GEDCOM tag: EMAIL",
    )
    website: str | None = Field(
        None,
        description="Website URL. GEDCOM tag: WWW",
    )
