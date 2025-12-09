"""GEDCOM data models.

This package provides Pydantic models for parsing and representing
GEDCOM 5.5.1 files, with full support for Ancestry.com export quirks.

Example usage:
    from pygedreader.models import Gedcom, Individual, Family

    # After parsing a GEDCOM file:
    gedcom = Gedcom(individuals=[...], families=[...])
    gedcom.resolve_references()

    # Access individuals
    person = gedcom.get_individual("@I123@")
    print(person.display_name)

    # Traverse relationships
    for fam_link in person.spouse_families:
        family = fam_link.family
        for child_link in family.children:
            print(child_link.individual.display_name)
"""

from .base import GedcomBaseModel, GedcomRecord, XRef
from .date import DateModifier, GedcomDate
from .event import Event, EventType, FamilyEvent
from .family import ChildLink, Family, SpouseLink
from .gedcom import Gedcom
from .header import GedcomVersion, Header, SourceSystem
from .individual import FamilyLink, Individual, MediaLink
from .media import MediaFile, MediaObject
from .name import Name
from .note import Note
from .place import Place
from .repository import Address, Repository
from .source import Source, SourcePublication
from .source_citation import SourceCitation, SourceData
from .submitter import Submitter

# Rebuild models to resolve forward references
# Must be done after all models are imported
SourceCitation.model_rebuild()
Name.model_rebuild()
Source.model_rebuild()
FamilyLink.model_rebuild()
MediaLink.model_rebuild()
SpouseLink.model_rebuild()
ChildLink.model_rebuild()
Individual.model_rebuild()
Family.model_rebuild()
Gedcom.model_rebuild()

__all__ = [
    # Base
    "GedcomBaseModel",
    "GedcomRecord",
    "XRef",
    # Date
    "GedcomDate",
    "DateModifier",
    # Place
    "Place",
    # Note
    "Note",
    # Source citation
    "SourceCitation",
    "SourceData",
    # Name
    "Name",
    # Event
    "Event",
    "FamilyEvent",
    "EventType",
    # Repository
    "Repository",
    "Address",
    # Submitter
    "Submitter",
    # Source
    "Source",
    "SourcePublication",
    # Media
    "MediaObject",
    "MediaFile",
    # Header
    "Header",
    "GedcomVersion",
    "SourceSystem",
    # Individual
    "Individual",
    "FamilyLink",
    "MediaLink",
    # Family
    "Family",
    "SpouseLink",
    "ChildLink",
    # Root container
    "Gedcom",
]
