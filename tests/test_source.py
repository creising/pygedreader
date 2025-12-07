"""Tests for GEDCOM source parsing."""

from parser import parse_string


class TestSourceBasics:
    """Tests for basic source parsing."""

    def test_parse_source(self, source_with_citations):
        """Parse source record."""
        gedcom = parse_string(source_with_citations)
        assert len(gedcom.sources) == 1

        src = gedcom.get_source("@S1@")
        assert src is not None
        assert src.xref == "@S1@"

    def test_source_title(self, source_with_citations):
        """Parse source title."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")
        assert src.title == "U.S. Census Records, 1900"

    def test_source_author(self, source_with_citations):
        """Parse source author."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")
        assert src.author == "U.S. Census Bureau"

    def test_source_publication(self, source_with_citations):
        """Parse source publication info."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")

        assert src.publication is not None
        assert src.publication.text == "Ancestry.com"
        assert src.publication.date is not None
        assert src.publication.date.year == 2010
        assert src.publication.place is not None
        assert src.publication.place.city == "Provo"


class TestSourceCitations:
    """Tests for source citations on records."""

    def test_event_source_citation(self, source_with_citations):
        """Parse source citation on event."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        assert indi.birth is not None
        assert len(indi.birth.sources) == 1

        citation = indi.birth.sources[0]
        assert citation.xref == "@S1@"
        assert citation.page == "Page 123, Line 45"

    def test_record_level_citation(self, source_with_citations):
        """Parse record-level source citation."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.sources) == 1
        citation = indi.sources[0]
        assert citation.xref == "@S1@"
        assert citation.page == "General reference"

    def test_citation_resolved_to_source(self, source_with_citations):
        """Source citations should resolve to Source objects."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        citation = indi.sources[0]
        assert citation.source is not None
        assert citation.source.xref == "@S1@"
        assert citation.source.title == "U.S. Census Records, 1900"


class TestAncestrySourceFeatures:
    """Tests for Ancestry.com source features."""

    def test_apid_on_citation(self, source_with_citations):
        """Parse _APID on source citation."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        # Citation on birth event
        citation = indi.birth.sources[0]
        assert "_APID" in citation.custom_tags
        # Custom tags are stored as lists
        assert "1,5678::9012" in citation.custom_tags["_APID"]

    def test_apid_on_source(self, ancestry_quirks_gedcom):
        """Parse _APID on source record."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        src = gedcom.get_source("@S1@")

        assert "_APID" in src.custom_tags
        # Custom tags are stored as lists
        assert "1,1234::0" in src.custom_tags["_APID"]


class TestRepositoryLink:
    """Tests for source-repository links."""

    def test_source_repo_xref(self, source_with_citations):
        """Parse REPO reference on source."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")

        assert src.repository_xref == "@R1@"

    def test_source_repo_resolved(self, source_with_citations):
        """Repository reference should resolve."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")

        assert src.repository is not None
        assert src.repository.xref == "@R1@"
        assert src.repository.name == "Ancestry.com"

    def test_repository_parsed(self, source_with_citations):
        """Parse repository record."""
        gedcom = parse_string(source_with_citations)
        assert len(gedcom.repositories) == 1

        repo = gedcom.get_repository("@R1@")
        assert repo is not None
        assert repo.name == "Ancestry.com"
