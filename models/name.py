"""GEDCOM name model.

Represents personal names with parsed components.

GEDCOM 5.5.1: PERSONAL_NAME_STRUCTURE
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#PERSONAL_NAME_STRUCTURE
"""

from __future__ import annotations

from pydantic import Field

from .base import GedcomBaseModel
from .source_citation import SourceCitation


class Name(GedcomBaseModel):
    """Represents a personal name with parsed components.

    GEDCOM 5.5.1: PERSONAL_NAME_STRUCTURE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#PERSONAL_NAME_STRUCTURE

    GEDCOM names use the format "Given /Surname/" where the surname
    is enclosed in slashes. An individual may have multiple names
    (birth name, married name, aliases, etc.).

    Attributes:
        full: Complete name as it appears in GEDCOM. GEDCOM tag: NAME
        first_name: Given/first name(s). GEDCOM tag: GIVN
        surname: Family name. GEDCOM tag: SURN
        prefix: Name prefix (Dr., Rev., etc.). GEDCOM tag: NPFX
        suffix: Name suffix (Jr., III, etc.). GEDCOM tag: NSFX
        nickname: Nickname or familiar name. GEDCOM tag: NICK
        name_type: Type of name (birth, married, aka, etc.). GEDCOM tag: TYPE
        sources: Source citations for this name. GEDCOM tag: SOUR
    """

    full: str = Field(
        ...,
        description="Complete name string. GEDCOM tag: NAME",
    )
    first_name: str | None = Field(
        None,
        description="Given/first name(s). GEDCOM tag: GIVN",
    )
    surname: str | None = Field(
        None,
        description="Family name. GEDCOM tag: SURN",
    )
    prefix: str | None = Field(
        None,
        description="Name prefix (Dr., Rev., etc.). GEDCOM tag: NPFX",
    )
    suffix: str | None = Field(
        None,
        description="Name suffix (Jr., III, etc.). GEDCOM tag: NSFX",
    )
    nickname: str | None = Field(
        None,
        description="Nickname or familiar name. GEDCOM tag: NICK",
    )
    name_type: str | None = Field(
        None,
        description="Type of name (birth, married, aka). GEDCOM tag: TYPE",
    )
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Source citations for this name. GEDCOM tag: SOUR",
    )

    @classmethod
    def from_string(cls, name_str: str) -> Name:
        """Parse a GEDCOM name string into components.

        GEDCOM format: "Given /Surname/" or "Given /Surname/ Suffix"

        Args:
            name_str: The raw name string from a GEDCOM file.

        Returns:
            Name with full text preserved and components parsed.
        """
        full = name_str.strip()
        first_name: str | None = None
        surname: str | None = None

        # Parse "Given /Surname/" format
        if "/" in full:
            parts = full.split("/")
            if len(parts) >= 2:
                # Text before first slash is given name
                first_name = parts[0].strip() or None
                # Text between slashes is surname
                surname = parts[1].strip() or None

        return cls(
            full=full,
            first_name=first_name,
            surname=surname,
        )

    def display_name(self) -> str:
        """Return a display-friendly name without slashes.

        Returns:
            Name formatted as "First Surname" or the full string if
            components weren't parsed.
        """
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.surname:
            parts.append(self.surname)
        return " ".join(parts) if parts else self.full

    def __str__(self) -> str:
        """Return the display name."""
        return self.display_name()
