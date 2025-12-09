"""GEDCOM root container model.

The top-level container for a parsed GEDCOM file with reference resolution.

GEDCOM 5.5.1: LINEAGE-LINKED GEDCOM
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field, PrivateAttr

from .base import GedcomBaseModel, XRef
from .family import Family
from .header import Header
from .individual import Individual
from .media import MediaObject
from .repository import Repository
from .source import Source
from .submitter import Submitter

if TYPE_CHECKING:
    from .source_citation import SourceCitation


class Gedcom(GedcomBaseModel):
    """Root container for a parsed GEDCOM file.

    GEDCOM 5.5.1: LINEAGE-LINKED GEDCOM
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html

    Contains all records organized by type with lookup dictionaries
    for efficient cross-reference resolution.

    Attributes:
        header: File header with metadata. GEDCOM tag: HEAD
        submitters: Submitter records. GEDCOM tag: SUBM
        individuals: Individual (person) records. GEDCOM tag: INDI
        families: Family records. GEDCOM tag: FAM
        sources: Source records. GEDCOM tag: SOUR
        repositories: Repository records. GEDCOM tag: REPO
        media_objects: Media object records. GEDCOM tag: OBJE
    """

    header: Header | None = Field(
        None,
        description="File header with metadata. GEDCOM tag: HEAD",
    )
    submitters: list[Submitter] = Field(
        default_factory=list,
        description="Submitter records. GEDCOM tag: SUBM",
    )
    individuals: list[Individual] = Field(
        default_factory=list,
        description="Individual (person) records. GEDCOM tag: INDI",
    )
    families: list[Family] = Field(
        default_factory=list,
        description="Family records. GEDCOM tag: FAM",
    )
    sources: list[Source] = Field(
        default_factory=list,
        description="Source records. GEDCOM tag: SOUR",
    )
    repositories: list[Repository] = Field(
        default_factory=list,
        description="Repository records. GEDCOM tag: REPO",
    )
    media_objects: list[MediaObject] = Field(
        default_factory=list,
        description="Media object records. GEDCOM tag: OBJE",
    )

    # Private lookup dictionaries (built lazily)
    _individuals_by_xref: dict[XRef, Individual] = PrivateAttr(default_factory=dict)
    _families_by_xref: dict[XRef, Family] = PrivateAttr(default_factory=dict)
    _sources_by_xref: dict[XRef, Source] = PrivateAttr(default_factory=dict)
    _repositories_by_xref: dict[XRef, Repository] = PrivateAttr(default_factory=dict)
    _media_by_xref: dict[XRef, MediaObject] = PrivateAttr(default_factory=dict)
    _lookups_built: bool = PrivateAttr(default=False)

    def _build_lookups(self) -> None:
        """Build lookup dictionaries for all records."""
        if self._lookups_built:
            return

        self._individuals_by_xref = {i.xref: i for i in self.individuals}
        self._families_by_xref = {f.xref: f for f in self.families}
        self._sources_by_xref = {s.xref: s for s in self.sources}
        self._repositories_by_xref = {r.xref: r for r in self.repositories}
        self._media_by_xref = {m.xref: m for m in self.media_objects}
        self._lookups_built = True

    def get_individual(self, xref: XRef) -> Individual | None:
        """Look up an individual by XREF.

        Args:
            xref: The individual's xref (e.g., "@I123@").

        Returns:
            The Individual record, or None if not found.
        """
        self._build_lookups()
        return self._individuals_by_xref.get(xref)

    def get_family(self, xref: XRef) -> Family | None:
        """Look up a family by XREF.

        Args:
            xref: The family's xref (e.g., "@F123@").

        Returns:
            The Family record, or None if not found.
        """
        self._build_lookups()
        return self._families_by_xref.get(xref)

    def get_source(self, xref: XRef) -> Source | None:
        """Look up a source by XREF.

        Args:
            xref: The source's xref (e.g., "@S123@").

        Returns:
            The Source record, or None if not found.
        """
        self._build_lookups()
        return self._sources_by_xref.get(xref)

    def get_repository(self, xref: XRef) -> Repository | None:
        """Look up a repository by XREF.

        Args:
            xref: The repository's xref (e.g., "@R123@").

        Returns:
            The Repository record, or None if not found.
        """
        self._build_lookups()
        return self._repositories_by_xref.get(xref)

    def get_media(self, xref: XRef) -> MediaObject | None:
        """Look up a media object by XREF.

        Args:
            xref: The media object's xref (e.g., "@O123@").

        Returns:
            The MediaObject record, or None if not found.
        """
        self._build_lookups()
        return self._media_by_xref.get(xref)

    def resolve_references(self) -> None:
        """Resolve all cross-references in the model tree.

        This populates the resolved object fields on link objects
        (e.g., FamilyLink.family, SpouseLink.individual, etc.).

        Should be called after parsing is complete.
        """
        self._build_lookups()

        # Resolve individual references
        for individual in self.individuals:
            # Resolve family links
            for fam_link in individual.parent_families:
                fam_link.family = self.get_family(fam_link.xref)
            for fam_link in individual.spouse_families:
                fam_link.family = self.get_family(fam_link.xref)

            # Resolve media links
            for media_link in individual.media:
                media_link.media = self.get_media(media_link.xref)

            # Resolve source citations
            self._resolve_source_citations(individual.sources)
            for name in individual.names:
                self._resolve_source_citations(name.sources)
            for event in individual.get_all_events():
                self._resolve_source_citations(event.sources)

        # Resolve family references
        for family in self.families:
            # Resolve spouse links
            for spouse_link in family.spouses:
                spouse_link.individual = self.get_individual(spouse_link.xref)

            # Resolve child links
            for child_link in family.children:
                child_link.individual = self.get_individual(child_link.xref)

            # Resolve source citations
            self._resolve_source_citations(family.sources)
            if family.marriage:
                self._resolve_source_citations(family.marriage.sources)
            if family.divorce:
                self._resolve_source_citations(family.divorce.sources)

        # Resolve source -> repository links
        for source in self.sources:
            if source.repository_xref:
                source.repository = self.get_repository(source.repository_xref)

    def _resolve_source_citations(
        self,
        citations: list[SourceCitation],  # noqa: F821
    ) -> None:
        """Resolve source references in a list of citations.

        Args:
            citations: List of SourceCitation objects to resolve.
        """
        for citation in citations:
            if citation.xref:
                citation.source = self.get_source(citation.xref)

    @property
    def stats(self) -> dict[str, int]:
        """Get statistics about the GEDCOM file.

        Returns:
            Dictionary with counts of each record type.
        """
        return {
            "individuals": len(self.individuals),
            "families": len(self.families),
            "sources": len(self.sources),
            "repositories": len(self.repositories),
            "media_objects": len(self.media_objects),
            "submitters": len(self.submitters),
        }
