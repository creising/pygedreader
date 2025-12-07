"""GEDCOM event and attribute models.

Represents life events (birth, death, marriage) and attributes (residence, occupation).

GEDCOM 5.5.1: INDIVIDUAL_EVENT_STRUCTURE, FAMILY_EVENT_STRUCTURE
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#INDIVIDUAL_EVENT_STRUCTURE
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field

from .base import GedcomBaseModel
from .date import GedcomDate
from .note import Note
from .place import Place
from .source_citation import SourceCitation


class EventType(str, Enum):
    """Standard GEDCOM event and attribute types.

    GEDCOM 5.5.1: INDIVIDUAL_EVENT_STRUCTURE, INDIVIDUAL_ATTRIBUTE_STRUCTURE,
    FAMILY_EVENT_STRUCTURE
    """

    # Individual events
    BIRTH = "BIRT"
    CHRISTENING = "CHR"
    DEATH = "DEAT"
    BURIAL = "BURI"
    CREMATION = "CREM"
    ADOPTION = "ADOP"
    BAPTISM = "BAPM"
    BAR_MITZVAH = "BARM"
    BAS_MITZVAH = "BASM"
    BLESSING = "BLES"
    ADULT_CHRISTENING = "CHRA"
    CONFIRMATION = "CONF"
    FIRST_COMMUNION = "FCOM"
    ORDINATION = "ORDN"
    NATURALIZATION = "NATU"
    EMIGRATION = "EMIG"
    IMMIGRATION = "IMMI"
    CENSUS = "CENS"
    PROBATE = "PROB"
    WILL = "WILL"
    GRADUATION = "GRAD"
    RETIREMENT = "RETI"
    EVENT = "EVEN"

    # Individual attributes
    RESIDENCE = "RESI"
    OCCUPATION = "OCCU"
    EDUCATION = "EDUC"
    RELIGION = "RELI"
    NATIONALITY = "NATI"
    TITLE = "TITL"
    CASTE = "CAST"
    PHYSICAL_DESCRIPTION = "DSCR"
    SSN = "SSN"
    NATIONAL_ID = "IDNO"

    # Family events
    MARRIAGE = "MARR"
    MARRIAGE_BANN = "MARB"
    MARRIAGE_CONTRACT = "MARC"
    MARRIAGE_LICENSE = "MARL"
    MARRIAGE_SETTLEMENT = "MARS"
    DIVORCE = "DIV"
    DIVORCE_FILED = "DIVF"
    ANNULMENT = "ANUL"
    ENGAGEMENT = "ENGA"


class Event(GedcomBaseModel):
    """Represents a life event or attribute.

    GEDCOM 5.5.1: INDIVIDUAL_EVENT_STRUCTURE, FAMILY_EVENT_STRUCTURE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#INDIVIDUAL_EVENT_STRUCTURE

    Events capture dated occurrences in a person's or family's life.
    Attributes are similar but represent ongoing states (residence, occupation).

    Ancestry-specific: The _MILT tag represents military service events
    and is stored with tag="_MILT".

    Attributes:
        tag: GEDCOM tag for this event (BIRT, DEAT, MARR, RESI, _MILT, etc.).
        event_type: Parsed EventType enum if this is a standard event.
        value: Optional value (e.g., "Y" for "1 DEAT Y"). GEDCOM tag value.
        date: When the event occurred. GEDCOM tag: DATE
        place: Where the event occurred. GEDCOM tag: PLAC
        type_detail: Sub-type or description. GEDCOM tag: TYPE
        cause: Cause (typically for death events). GEDCOM tag: CAUS
        age: Age at the time of event. GEDCOM tag: AGE
        agency: Responsible agency. GEDCOM tag: AGNC
        sources: Source citations. GEDCOM tag: SOUR
        notes: Notes about this event. GEDCOM tag: NOTE
        adopted_by: For adoption events, who adopted (HUSB, WIFE, BOTH). GEDCOM tag: ADOP
    """

    tag: str = Field(
        ...,
        description="GEDCOM tag (BIRT, DEAT, MARR, RESI, _MILT, etc.).",
    )
    event_type: Optional[EventType] = Field(
        None,
        description="Parsed EventType enum for standard events.",
    )
    value: Optional[str] = Field(
        None,
        description="Optional tag value (e.g., 'Y' for '1 DEAT Y').",
    )
    date: Optional[GedcomDate] = Field(
        None,
        description="When the event occurred. GEDCOM tag: DATE",
    )
    place: Optional[Place] = Field(
        None,
        description="Where the event occurred. GEDCOM tag: PLAC",
    )
    type_detail: Optional[str] = Field(
        None,
        description="Sub-type or description. GEDCOM tag: TYPE",
    )
    cause: Optional[str] = Field(
        None,
        description="Cause (typically for death). GEDCOM tag: CAUS",
    )
    age: Optional[str] = Field(
        None,
        description="Age at time of event. GEDCOM tag: AGE",
    )
    agency: Optional[str] = Field(
        None,
        description="Responsible agency. GEDCOM tag: AGNC",
    )
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Source citations. GEDCOM tag: SOUR",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="Notes about this event. GEDCOM tag: NOTE",
    )
    adopted_by: Optional[str] = Field(
        None,
        description="For adoption: HUSB, WIFE, or BOTH. GEDCOM tag: ADOP",
    )

    @property
    def is_custom(self) -> bool:
        """Check if this is a custom (non-standard) event.

        Returns:
            True if the tag starts with underscore (Ancestry custom tags).
        """
        return self.tag.startswith("_")

    @classmethod
    def from_tag(cls, tag: str, value: Optional[str] = None) -> Event:
        """Create an Event from a GEDCOM tag.

        Args:
            tag: The GEDCOM tag (BIRT, DEAT, _MILT, etc.).
            value: Optional value associated with the tag.

        Returns:
            Event with tag set and event_type parsed if standard.
        """
        event_type: Optional[EventType] = None
        try:
            event_type = EventType(tag)
        except ValueError:
            pass

        return cls(
            tag=tag,
            event_type=event_type,
            value=value,
        )


class FamilyEvent(Event):
    """Event that belongs to a family (FAM record).

    GEDCOM 5.5.1: FAMILY_EVENT_STRUCTURE

    Family events like marriage can include age information for both spouses.

    Attributes:
        spouse1_age: Age of first spouse at event. GEDCOM tag: HUSB.AGE
        spouse2_age: Age of second spouse at event. GEDCOM tag: WIFE.AGE
    """

    spouse1_age: Optional[str] = Field(
        None,
        description="Age of first spouse. GEDCOM tag: HUSB.AGE",
    )
    spouse2_age: Optional[str] = Field(
        None,
        description="Age of second spouse. GEDCOM tag: WIFE.AGE",
    )
