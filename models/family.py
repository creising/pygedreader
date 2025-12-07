"""GEDCOM family model.

Represents a family unit (spouses and children).

GEDCOM 5.5.1: FAM_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#FAM_RECORD
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import GedcomBaseModel, GedcomRecord, XRef
from .event import FamilyEvent
from .note import Note
from .source_citation import SourceCitation

if TYPE_CHECKING:
    from .individual import Individual


class SpouseLink(GedcomBaseModel):
    """Link to a spouse in the family.

    Note: GEDCOM uses HUSB/WIFE tags, but we use gender-neutral
    storage. The original role is preserved for reference.

    Attributes:
        xref: Reference to INDI record. GEDCOM tag: HUSB or WIFE
        individual: Resolved Individual object (populated after parsing).
        role: Original GEDCOM role (HUSB or WIFE) for reference.
    """

    xref: XRef = Field(
        ...,
        description="Reference to INDI record. GEDCOM tag: HUSB or WIFE",
    )
    individual: Individual | None = Field(
        None,
        exclude=True,
        description="Resolved Individual object (populated after parsing).",
    )
    role: str = Field(
        ...,
        description="Original GEDCOM role: HUSB or WIFE.",
    )


class ChildLink(GedcomBaseModel):
    """Link to a child in the family.

    Ancestry-specific: _FREL and _MREL custom tags indicate
    relationship type to father/mother (stored in custom_tags).

    Attributes:
        xref: Reference to INDI record. GEDCOM tag: CHIL
        individual: Resolved Individual object (populated after parsing).
    """

    xref: XRef = Field(
        ...,
        description="Reference to INDI record. GEDCOM tag: CHIL",
    )
    individual: Individual | None = Field(
        None,
        exclude=True,
        description="Resolved Individual object (populated after parsing).",
    )


class Family(GedcomRecord):
    """Represents a family unit.

    GEDCOM 5.5.1: FAM_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#FAM_RECORD

    A family consists of spouses (partners) and their children.
    GEDCOM uses HUSB/WIFE tags but we store spouses in a gender-neutral
    list while preserving the original role.

    Ancestry-specific custom tags on marriage sources:
    - _HPID: Husband Person ID
    - _WPID: Wife Person ID

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @F123@
        spouses: Spouse/partner links. GEDCOM tags: HUSB, WIFE
        children: Child links. GEDCOM tag: CHIL
        marriage: Marriage event. GEDCOM tag: MARR
        divorce: Divorce event. GEDCOM tag: DIV
        annulment: Annulment event. GEDCOM tag: ANUL
        engagement: Engagement event. GEDCOM tag: ENGA
        other_events: Other family events.
        sources: Record-level source citations. GEDCOM tag: SOUR
        notes: Notes about this family. GEDCOM tag: NOTE
    """

    spouses: list[SpouseLink] = Field(
        default_factory=list,
        description="Spouse/partner links. GEDCOM tags: HUSB, WIFE",
    )
    children: list[ChildLink] = Field(
        default_factory=list,
        description="Child links. GEDCOM tag: CHIL",
    )

    # Family events
    marriage: FamilyEvent | None = Field(
        None,
        description="Marriage event. GEDCOM tag: MARR",
    )
    divorce: FamilyEvent | None = Field(
        None,
        description="Divorce event. GEDCOM tag: DIV",
    )
    annulment: FamilyEvent | None = Field(
        None,
        description="Annulment event. GEDCOM tag: ANUL",
    )
    engagement: FamilyEvent | None = Field(
        None,
        description="Engagement event. GEDCOM tag: ENGA",
    )

    # Other family events
    other_events: list[FamilyEvent] = Field(
        default_factory=list,
        description="Other family events.",
    )

    # Record-level citations and notes
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Record-level source citations. GEDCOM tag: SOUR",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="Notes about this family. GEDCOM tag: NOTE",
    )

    @property
    def spouse_xrefs(self) -> list[XRef]:
        """Get all spouse XREFs.

        Returns:
            List of spouse INDI xrefs.
        """
        return [s.xref for s in self.spouses]

    @property
    def child_xrefs(self) -> list[XRef]:
        """Get all child XREFs.

        Returns:
            List of child INDI xrefs.
        """
        return [c.xref for c in self.children]

    def get_spouse_by_role(self, role: str) -> SpouseLink | None:
        """Get spouse by their original GEDCOM role.

        Args:
            role: The GEDCOM role ("HUSB" or "WIFE").

        Returns:
            The SpouseLink with matching role, or None.
        """
        for spouse in self.spouses:
            if spouse.role == role:
                return spouse
        return None
