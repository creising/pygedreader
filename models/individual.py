"""GEDCOM individual (person) model.

Represents a person in the family tree.

GEDCOM 5.5.1: INDIVIDUAL_RECORD
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#INDIVIDUAL_RECORD
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .base import GedcomBaseModel, GedcomRecord, XRef
from .event import Event
from .name import Name
from .note import Note
from .source_citation import SourceCitation

if TYPE_CHECKING:
    from .family import Family
    from .media import MediaObject


class FamilyLink(GedcomBaseModel):
    """Link to a family record.

    Represents either FAMC (family as child) or FAMS (family as spouse).

    Ancestry-specific: _FREL and _MREL custom tags indicate
    relationship type to father/mother (stored in custom_tags).

    Attributes:
        xref: Reference to FAM record. GEDCOM tag: FAMC or FAMS
        family: Resolved Family object (populated after parsing).
        pedigree: Pedigree type (birth, adopted, foster). GEDCOM tag: PEDI
        status: Link status. GEDCOM tag: STAT
    """

    xref: XRef = Field(
        ...,
        description="Reference to FAM record. GEDCOM tag: FAMC or FAMS",
    )
    family: Optional["Family"] = Field(
        None,
        exclude=True,
        description="Resolved Family object (populated after parsing).",
    )
    pedigree: Optional[str] = Field(
        None,
        description="Pedigree: birth, adopted, foster, sealing. GEDCOM tag: PEDI",
    )
    status: Optional[str] = Field(
        None,
        description="Link status. GEDCOM tag: STAT",
    )


class MediaLink(GedcomBaseModel):
    """Link to a media object.

    Attributes:
        xref: Reference to OBJE record. GEDCOM tag: OBJE
        media: Resolved MediaObject (populated after parsing).
        is_primary: Whether this is the primary media. GEDCOM tag: _PRIM
    """

    xref: XRef = Field(
        ...,
        description="Reference to OBJE record. GEDCOM tag: OBJE",
    )
    media: Optional["MediaObject"] = Field(
        None,
        exclude=True,
        description="Resolved MediaObject (populated after parsing).",
    )
    is_primary: bool = Field(
        False,
        description="Whether this is primary media. GEDCOM tag: _PRIM",
    )


class Individual(GedcomRecord):
    """Represents an individual person.

    GEDCOM 5.5.1: INDIVIDUAL_RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#INDIVIDUAL_RECORD

    Ancestry-specific quirks handled:
    - MARR events appear under INDI (should be under FAM per spec)
    - SEX tag can have nested SOUR citations

    Attributes:
        xref: Unique identifier (inherited). GEDCOM format: @I123@
        names: Person's names (may have multiple). GEDCOM tag: NAME
        sex: Biological sex (M, F, U, X). GEDCOM tag: SEX
        sex_sources: Sources for sex (Ancestry quirk). GEDCOM tag: SOUR under SEX
        birth: Birth event. GEDCOM tag: BIRT
        death: Death event. GEDCOM tag: DEAT
        christening: Christening event. GEDCOM tag: CHR
        burial: Burial event. GEDCOM tag: BURI
        residences: Residence events/attributes. GEDCOM tag: RESI
        occupations: Occupation attributes. GEDCOM tag: OCCU
        education: Education attributes. GEDCOM tag: EDUC
        marriages: Marriage events on INDI (Ancestry quirk). GEDCOM tag: MARR
        custom_events: Custom events like _MILT. GEDCOM tag: _*
        other_events: Other standard events.
        parent_families: Families where this person is a child. GEDCOM tag: FAMC
        spouse_families: Families where this person is a spouse. GEDCOM tag: FAMS
        media: Linked media objects. GEDCOM tag: OBJE
        sources: Record-level source citations. GEDCOM tag: SOUR
        notes: Notes about this person. GEDCOM tag: NOTE
    """

    names: list[Name] = Field(
        default_factory=list,
        description="Person's names (birth, married, aka). GEDCOM tag: NAME",
    )
    sex: Optional[str] = Field(
        None,
        description="Biological sex: M, F, U (unknown), X. GEDCOM tag: SEX",
    )
    sex_sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Sources for sex (Ancestry quirk). GEDCOM tag: SOUR under SEX",
    )

    # Life events
    birth: Optional[Event] = Field(
        None,
        description="Birth event. GEDCOM tag: BIRT",
    )
    death: Optional[Event] = Field(
        None,
        description="Death event. GEDCOM tag: DEAT",
    )
    christening: Optional[Event] = Field(
        None,
        description="Christening event. GEDCOM tag: CHR",
    )
    burial: Optional[Event] = Field(
        None,
        description="Burial event. GEDCOM tag: BURI",
    )

    # Repeatable events/attributes
    residences: list[Event] = Field(
        default_factory=list,
        description="Residence events. GEDCOM tag: RESI",
    )
    occupations: list[Event] = Field(
        default_factory=list,
        description="Occupation attributes. GEDCOM tag: OCCU",
    )
    education: list[Event] = Field(
        default_factory=list,
        description="Education attributes. GEDCOM tag: EDUC",
    )

    # Ancestry quirk: MARR on INDI instead of FAM
    marriages: list[Event] = Field(
        default_factory=list,
        description="Marriage events on INDI (Ancestry quirk). GEDCOM tag: MARR",
    )

    # Custom events (e.g., _MILT for military)
    custom_events: list[Event] = Field(
        default_factory=list,
        description="Custom events (e.g., _MILT). GEDCOM tag: _*",
    )

    # Other standard events
    other_events: list[Event] = Field(
        default_factory=list,
        description="Other standard events.",
    )

    # Family links
    parent_families: list[FamilyLink] = Field(
        default_factory=list,
        description="Families where person is a child. GEDCOM tag: FAMC",
    )
    spouse_families: list[FamilyLink] = Field(
        default_factory=list,
        description="Families where person is a spouse. GEDCOM tag: FAMS",
    )

    # Media
    media: list[MediaLink] = Field(
        default_factory=list,
        description="Linked media objects. GEDCOM tag: OBJE",
    )

    # Record-level citations and notes
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Record-level source citations. GEDCOM tag: SOUR",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="Notes about this person. GEDCOM tag: NOTE",
    )

    @property
    def primary_name(self) -> Optional[Name]:
        """Get the primary (first) name.

        Returns:
            The first name in the names list, or None if no names.
        """
        return self.names[0] if self.names else None

    @property
    def display_name(self) -> str:
        """Get a display-friendly name.

        Returns:
            The primary name formatted for display, or the xref if no names.
        """
        if self.primary_name:
            return self.primary_name.display_name()
        return self.xref

    def get_all_events(self) -> list[Event]:
        """Get all events for this individual.

        Returns:
            List of all events (birth, death, residences, etc.).
        """
        events: list[Event] = []
        if self.birth:
            events.append(self.birth)
        if self.death:
            events.append(self.death)
        if self.christening:
            events.append(self.christening)
        if self.burial:
            events.append(self.burial)
        events.extend(self.residences)
        events.extend(self.occupations)
        events.extend(self.education)
        events.extend(self.marriages)
        events.extend(self.custom_events)
        events.extend(self.other_events)
        return events
