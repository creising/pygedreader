"""GEDCOM record parsers.

Converts GedcomNode trees into Pydantic model objects.
"""

from __future__ import annotations

from typing import Any

from models import (
    Address,
    ChildLink,
    Event,
    FamilyEvent,
    FamilyLink,
    GedcomDate,
    GedcomVersion,
    MediaFile,
    MediaLink,
    Name,
    Note,
    Place,
    Source,
    SourceCitation,
    SourceData,
    SourcePublication,
    SourceSystem,
    SpouseLink,
)
from models.family import Family
from models.header import Header
from models.individual import Individual
from models.media import MediaObject
from models.repository import Repository
from models.submitter import Submitter

from .tree import GedcomNode


def parse_date(node: GedcomNode | None) -> GedcomDate | None:
    """Parse a DATE node into a GedcomDate."""
    if node is None or node.value is None:
        return None
    return GedcomDate.from_string(node.value)


def parse_place(node: GedcomNode | None) -> Place | None:
    """Parse a PLAC node into a Place."""
    if node is None or node.value is None:
        return None

    place = Place.from_string(node.value)

    # Check for MAP coordinates
    map_node = node.get_child("MAP")
    if map_node:
        lati = map_node.get_child_value("LATI")
        long = map_node.get_child_value("LONG")
        if lati:
            try:
                # GEDCOM uses N/S prefix, convert to signed
                place.latitude = _parse_coordinate(lati)
            except ValueError:
                pass
        if long:
            try:
                place.longitude = _parse_coordinate(long)
            except ValueError:
                pass

    # Collect custom tags
    place.custom_tags = _collect_custom_tags(node)

    return place


def _parse_coordinate(value: str) -> float:
    """Parse a GEDCOM coordinate (N123.45 or S123.45)."""
    value = value.strip().upper()
    if value.startswith(("N", "E")):
        return float(value[1:])
    elif value.startswith(("S", "W")):
        return -float(value[1:])
    return float(value)


def parse_note(node: GedcomNode) -> Note:
    """Parse a NOTE node into a Note."""
    text = node.get_text_with_continuations()
    xref = node.value if node.value and node.value.startswith("@") else None

    note = Note.from_string(text, xref=xref)
    note.custom_tags = _collect_custom_tags(node)

    return note


def parse_source_data(node: GedcomNode) -> SourceData:
    """Parse a DATA node within a source citation."""
    data = SourceData(
        date=node.get_child_value("DATE"),
        text=node.get_child_value("TEXT"),
        www=node.get_child_value("WWW"),
    )
    data.custom_tags = _collect_custom_tags(node)
    return data


def parse_source_citation(node: GedcomNode) -> SourceCitation:
    """Parse an inline SOUR citation."""
    # SOUR can be either @XREF@ reference or inline text
    xref = None
    if node.value and node.value.startswith("@"):
        xref = node.value

    citation = SourceCitation(
        xref=xref,
        page=node.get_child_value("PAGE"),
        quality=_parse_int(node.get_child_value("QUAY")),
    )

    # Parse DATA sub-record
    data_node = node.get_child("DATA")
    if data_node:
        citation.data = parse_source_data(data_node)

    # Parse notes
    for note_node in node.get_children("NOTE"):
        citation.notes.append(note_node.get_text_with_continuations())

    citation.custom_tags = _collect_custom_tags(node)

    return citation


def parse_name(node: GedcomNode) -> Name:
    """Parse a NAME node into a Name."""
    name = Name.from_string(node.value or "")

    # Override with explicit components if present
    name.first_name = node.get_child_value("GIVN") or name.first_name
    name.surname = node.get_child_value("SURN") or name.surname
    name.prefix = node.get_child_value("NPFX")
    name.suffix = node.get_child_value("NSFX")
    name.nickname = node.get_child_value("NICK")
    name.name_type = node.get_child_value("TYPE")

    # Parse source citations
    for sour_node in node.get_children("SOUR"):
        name.sources.append(parse_source_citation(sour_node))

    name.custom_tags = _collect_custom_tags(node)

    return name


def parse_event(node: GedcomNode) -> Event:
    """Parse an event node (BIRT, DEAT, RESI, etc.) into an Event."""
    event = Event.from_tag(node.tag, node.value)

    event.date = parse_date(node.get_child("DATE"))
    event.place = parse_place(node.get_child("PLAC"))
    event.type_detail = node.get_child_value("TYPE")
    event.cause = node.get_child_value("CAUS")
    event.age = node.get_child_value("AGE")
    event.agency = node.get_child_value("AGNC")

    # For adoption events
    event.adopted_by = node.get_child_value("ADOP")

    # Parse source citations
    for sour_node in node.get_children("SOUR"):
        event.sources.append(parse_source_citation(sour_node))

    # Parse notes
    for note_node in node.get_children("NOTE"):
        event.notes.append(parse_note(note_node))

    event.custom_tags = _collect_custom_tags(node)

    return event


def parse_family_event(node: GedcomNode) -> FamilyEvent:
    """Parse a family event node (MARR, DIV, etc.)."""
    base_event = parse_event(node)

    event = FamilyEvent(
        tag=base_event.tag,
        event_type=base_event.event_type,
        value=base_event.value,
        date=base_event.date,
        place=base_event.place,
        type_detail=base_event.type_detail,
        cause=base_event.cause,
        age=base_event.age,
        agency=base_event.agency,
        sources=base_event.sources,
        notes=base_event.notes,
        custom_tags=base_event.custom_tags,
    )

    # Parse spouse ages
    husb_node = node.get_child("HUSB")
    if husb_node:
        event.spouse1_age = husb_node.get_child_value("AGE")

    wife_node = node.get_child("WIFE")
    if wife_node:
        event.spouse2_age = wife_node.get_child_value("AGE")

    return event


def parse_individual(node: GedcomNode) -> Individual:
    """Parse an INDI node into an Individual."""
    if not node.xref:
        raise ValueError(f"INDI record missing xref at line {node.line_number}")

    individual = Individual(xref=node.xref)

    # Parse names
    for name_node in node.get_children("NAME"):
        individual.names.append(parse_name(name_node))

    # Parse sex
    sex_node = node.get_child("SEX")
    if sex_node:
        individual.sex = sex_node.value
        # Ancestry quirk: SEX can have SOUR children
        for sour_node in sex_node.get_children("SOUR"):
            individual.sex_sources.append(parse_source_citation(sour_node))

    # Parse events
    _parse_individual_events(node, individual)

    # Parse family links
    for famc_node in node.get_children("FAMC"):
        if famc_node.value:
            link = FamilyLink(xref=famc_node.value)
            link.pedigree = famc_node.get_child_value("PEDI")
            link.status = famc_node.get_child_value("STAT")
            link.custom_tags = _collect_custom_tags(famc_node)
            individual.parent_families.append(link)

    for fams_node in node.get_children("FAMS"):
        if fams_node.value:
            link = FamilyLink(xref=fams_node.value)
            link.custom_tags = _collect_custom_tags(fams_node)
            individual.spouse_families.append(link)

    # Parse media links
    for obje_node in node.get_children("OBJE"):
        if obje_node.value and obje_node.value.startswith("@"):
            media_link = MediaLink(xref=obje_node.value)
            prim = obje_node.get_child_value("_PRIM")
            media_link.is_primary = prim == "Y" if prim else False
            media_link.custom_tags = _collect_custom_tags(obje_node)
            individual.media.append(media_link)

    # Parse record-level source citations
    for sour_node in node.get_children("SOUR"):
        individual.sources.append(parse_source_citation(sour_node))

    # Parse notes
    for note_node in node.get_children("NOTE"):
        individual.notes.append(parse_note(note_node))

    individual.custom_tags = _collect_custom_tags(node)

    return individual


def _parse_individual_events(node: GedcomNode, individual: Individual) -> None:
    """Parse all events from an INDI node."""
    # Single events
    event_map = {
        "BIRT": "birth",
        "DEAT": "death",
        "CHR": "christening",
        "BURI": "burial",
    }

    for tag, attr in event_map.items():
        event_node = node.get_child(tag)
        if event_node:
            setattr(individual, attr, parse_event(event_node))

    # Repeatable events
    for resi_node in node.get_children("RESI"):
        individual.residences.append(parse_event(resi_node))

    for occu_node in node.get_children("OCCU"):
        individual.occupations.append(parse_event(occu_node))

    for educ_node in node.get_children("EDUC"):
        individual.education.append(parse_event(educ_node))

    # Ancestry quirk: MARR under INDI
    for marr_node in node.get_children("MARR"):
        individual.marriages.append(parse_event(marr_node))

    # Custom events (e.g., _MILT)
    for child in node.children:
        if child.tag.startswith("_") and _is_event_like(child):
            individual.custom_events.append(parse_event(child))

    # Other standard events
    other_event_tags = {
        "BAPM",
        "BARM",
        "BASM",
        "BLES",
        "CHRA",
        "CONF",
        "FCOM",
        "ORDN",
        "NATU",
        "EMIG",
        "IMMI",
        "CENS",
        "PROB",
        "WILL",
        "GRAD",
        "RETI",
        "EVEN",
        "ADOP",
        "CREM",
    }
    for child in node.children:
        if child.tag in other_event_tags:
            individual.other_events.append(parse_event(child))


def _is_event_like(node: GedcomNode) -> bool:
    """Check if a custom tag node looks like an event (has DATE or PLAC)."""
    return node.get_child("DATE") is not None or node.get_child("PLAC") is not None


def parse_family(node: GedcomNode) -> Family:
    """Parse a FAM node into a Family."""
    if not node.xref:
        raise ValueError(f"FAM record missing xref at line {node.line_number}")

    family = Family(xref=node.xref)

    # Parse spouses
    husb_node = node.get_child("HUSB")
    if husb_node and husb_node.value:
        family.spouses.append(SpouseLink(xref=husb_node.value, role="HUSB"))

    wife_node = node.get_child("WIFE")
    if wife_node and wife_node.value:
        family.spouses.append(SpouseLink(xref=wife_node.value, role="WIFE"))

    # Parse children
    for chil_node in node.get_children("CHIL"):
        if chil_node.value:
            child_link = ChildLink(xref=chil_node.value)
            child_link.custom_tags = _collect_custom_tags(chil_node)
            family.children.append(child_link)

    # Parse events
    marr_node = node.get_child("MARR")
    if marr_node:
        family.marriage = parse_family_event(marr_node)

    div_node = node.get_child("DIV")
    if div_node:
        family.divorce = parse_family_event(div_node)

    anul_node = node.get_child("ANUL")
    if anul_node:
        family.annulment = parse_family_event(anul_node)

    enga_node = node.get_child("ENGA")
    if enga_node:
        family.engagement = parse_family_event(enga_node)

    # Other family events
    other_event_tags = {"MARB", "MARC", "MARL", "MARS", "DIVF", "EVEN"}
    for child in node.children:
        if child.tag in other_event_tags:
            family.other_events.append(parse_family_event(child))

    # Parse source citations
    for sour_node in node.get_children("SOUR"):
        family.sources.append(parse_source_citation(sour_node))

    # Parse notes
    for note_node in node.get_children("NOTE"):
        family.notes.append(parse_note(note_node))

    family.custom_tags = _collect_custom_tags(node)

    return family


def parse_source(node: GedcomNode) -> Source:
    """Parse a SOUR record into a Source."""
    if not node.xref:
        raise ValueError(f"SOUR record missing xref at line {node.line_number}")

    source = Source(xref=node.xref)

    source.title = node.get_child_value("TITL")
    source.author = node.get_child_value("AUTH")
    source.abbreviation = node.get_child_value("ABBR")

    # Parse publication
    publ_node = node.get_child("PUBL")
    if publ_node:
        source.publication = SourcePublication(
            text=publ_node.get_text_with_continuations(),
            date=parse_date(publ_node.get_child("DATE")),
            place=parse_place(publ_node.get_child("PLAC")),
        )

    # Repository reference
    repo_node = node.get_child("REPO")
    if repo_node and repo_node.value:
        source.repository_xref = repo_node.value

    # Parse notes
    for note_node in node.get_children("NOTE"):
        source.notes.append(parse_note(note_node))

    source.custom_tags = _collect_custom_tags(node)

    return source


def parse_repository(node: GedcomNode) -> Repository:
    """Parse a REPO record into a Repository."""
    if not node.xref:
        raise ValueError(f"REPO record missing xref at line {node.line_number}")

    name = node.get_child_value("NAME")
    if not name:
        name = "Unknown Repository"

    repo = Repository(xref=node.xref, name=name)

    # Parse address
    addr_node = node.get_child("ADDR")
    if addr_node:
        repo.address = Address(
            full=addr_node.get_text_with_continuations(),
            line1=addr_node.get_child_value("ADR1"),
            line2=addr_node.get_child_value("ADR2"),
            city=addr_node.get_child_value("CITY"),
            state=addr_node.get_child_value("STAE"),
            postal_code=addr_node.get_child_value("POST"),
            country=addr_node.get_child_value("CTRY"),
        )

    repo.phone = node.get_child_value("PHON")
    repo.email = node.get_child_value("EMAIL")
    repo.website = node.get_child_value("WWW")

    repo.custom_tags = _collect_custom_tags(node)

    return repo


def parse_media_object(node: GedcomNode) -> MediaObject:
    """Parse an OBJE record into a MediaObject."""
    if not node.xref:
        raise ValueError(f"OBJE record missing xref at line {node.line_number}")

    media = MediaObject(xref=node.xref)

    # Parse file info
    file_node = node.get_child("FILE")
    if file_node:
        media.file = MediaFile(path=file_node.value)

        form_node = file_node.get_child("FORM")
        if form_node:
            media.file.format = form_node.value
            media.file.media_type = form_node.get_child_value("TYPE")
            media.file.custom_tags = _collect_custom_tags(form_node)

        media.file.title = file_node.get_child_value("TITL")

    media.date = parse_date(node.get_child("DATE"))
    media.place = parse_place(node.get_child("PLAC"))

    media.custom_tags = _collect_custom_tags(node)

    return media


def parse_submitter(node: GedcomNode) -> Submitter:
    """Parse a SUBM record into a Submitter."""
    if not node.xref:
        raise ValueError(f"SUBM record missing xref at line {node.line_number}")

    name = node.get_child_value("NAME")
    if not name:
        name = "Unknown Submitter"

    submitter = Submitter(xref=node.xref, name=name)

    addr_node = node.get_child("ADDR")
    if addr_node:
        submitter.address = addr_node.get_text_with_continuations()

    submitter.phone = node.get_child_value("PHON")
    submitter.email = node.get_child_value("EMAIL")
    submitter.website = node.get_child_value("WWW")

    submitter.custom_tags = _collect_custom_tags(node)

    return submitter


def parse_header(node: GedcomNode) -> Header:
    """Parse a HEAD record into a Header."""
    header = Header()

    # Parse source system
    sour_node = node.get_child("SOUR")
    if sour_node:
        header.source = SourceSystem(
            system_id=sour_node.value or "UNKNOWN",
            name=sour_node.get_child_value("NAME"),
            version=sour_node.get_child_value("VERS"),
        )

        corp_node = sour_node.get_child("CORP")
        if corp_node:
            header.source.corporation = corp_node.value
            header.source.phone = corp_node.get_child_value("PHON")
            header.source.website = corp_node.get_child_value("WWW")

            addr_node = corp_node.get_child("ADDR")
            if addr_node:
                header.source.address = addr_node.get_text_with_continuations()

        header.source.custom_tags = _collect_custom_tags(sour_node)

    # Parse date/time
    header.date = parse_date(node.get_child("DATE"))
    date_node = node.get_child("DATE")
    if date_node:
        header.time = date_node.get_child_value("TIME")

    # Submitter reference
    subm_node = node.get_child("SUBM")
    if subm_node and subm_node.value:
        header.submitter_xref = subm_node.value

    # GEDCOM version
    gedc_node = node.get_child("GEDC")
    if gedc_node:
        header.gedcom_version = GedcomVersion(
            version=gedc_node.get_child_value("VERS") or "5.5.1",
            form=gedc_node.get_child_value("FORM") or "LINEAGE-LINKED",
        )

    header.charset = node.get_child_value("CHAR") or "UTF-8"
    header.language = node.get_child_value("LANG")
    header.filename = node.get_child_value("FILE")

    # Notes
    for note_node in node.get_children("NOTE"):
        header.notes.append(note_node.get_text_with_continuations())

    header.custom_tags = _collect_custom_tags(node)

    return header


def _collect_custom_tags(node: GedcomNode) -> dict[str, list[Any]]:
    """Collect all custom underscore-prefixed tags from a node."""
    custom_tags: dict[str, list[Any]] = {}

    for child in node.children:
        if child.tag.startswith("_"):
            if child.tag not in custom_tags:
                custom_tags[child.tag] = []

            # For simple values, just store the value
            # For complex structures, store the node's text with continuations
            if child.children:
                # Has nested structure - store as dict
                value: Any = {
                    "value": child.value,
                    "children": _collect_custom_tags(child),
                }
                # Include any specific child values
                for subchild in child.children:
                    if not subchild.tag.startswith("_"):
                        value[subchild.tag] = subchild.get_text_with_continuations()
            else:
                value = child.value

            custom_tags[child.tag].append(value)

    return custom_tags


def _parse_int(value: str | None) -> int | None:
    """Safely parse an integer value."""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
