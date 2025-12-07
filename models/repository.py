"""GEDCOM repository model.

Represents archives, libraries, or other repositories holding source documents.

GEDCOM 5.5.1: REPOSITORY_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#REPOSITORY_RECORD
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import GedcomBaseModel, GedcomRecord


class Address(GedcomBaseModel):
    """Represents a postal address.

    GEDCOM 5.5.1: ADDRESS_STRUCTURE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#ADDRESS_STRUCTURE

    Addresses may span multiple lines using CONT tags in GEDCOM.

    Attributes:
        full: Complete address as a single string. GEDCOM tag: ADDR (with CONT)
        line1: First address line. GEDCOM tag: ADR1
        line2: Second address line. GEDCOM tag: ADR2
        city: City. GEDCOM tag: CITY
        state: State or province. GEDCOM tag: STAE
        postal_code: Postal/ZIP code. GEDCOM tag: POST
        country: Country. GEDCOM tag: CTRY
    """

    full: str = Field(
        ...,
        description="Complete address text. GEDCOM tag: ADDR",
    )
    line1: Optional[str] = Field(
        None,
        description="First address line. GEDCOM tag: ADR1",
    )
    line2: Optional[str] = Field(
        None,
        description="Second address line. GEDCOM tag: ADR2",
    )
    city: Optional[str] = Field(
        None,
        description="City. GEDCOM tag: CITY",
    )
    state: Optional[str] = Field(
        None,
        description="State or province. GEDCOM tag: STAE",
    )
    postal_code: Optional[str] = Field(
        None,
        description="Postal/ZIP code. GEDCOM tag: POST",
    )
    country: Optional[str] = Field(
        None,
        description="Country. GEDCOM tag: CTRY",
    )


class Repository(GedcomRecord):
    """Represents a repository (archive, library, etc.).

    GEDCOM 5.5.1: REPOSITORY_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#REPOSITORY_RECORD

    Repositories are referenced by Source records to indicate where
    the original source documents are held.

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @R123@
        name: Repository name. GEDCOM tag: NAME
        address: Postal address. GEDCOM tag: ADDR
        phone: Phone number. GEDCOM tag: PHON
        email: Email address. GEDCOM tag: EMAIL
        website: Website URL. GEDCOM tag: WWW
    """

    name: str = Field(
        ...,
        description="Repository name. GEDCOM tag: NAME",
    )
    address: Optional[Address] = Field(
        None,
        description="Postal address. GEDCOM tag: ADDR",
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number. GEDCOM tag: PHON",
    )
    email: Optional[str] = Field(
        None,
        description="Email address. GEDCOM tag: EMAIL",
    )
    website: Optional[str] = Field(
        None,
        description="Website URL. GEDCOM tag: WWW",
    )
