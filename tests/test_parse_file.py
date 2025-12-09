"""Tests for full GEDCOM file parsing."""

from pygedreader import parse_string


class TestMinimalGedcom:
    """Tests for minimal valid GEDCOM files."""

    def test_parse_minimal(self, minimal_gedcom):
        """Parse minimal valid GEDCOM."""
        gedcom = parse_string(minimal_gedcom)

        assert gedcom.header is not None
        assert len(gedcom.individuals) == 1
        assert len(gedcom.families) == 0

    def test_header_parsed(self, minimal_gedcom):
        """Header should be parsed."""
        gedcom = parse_string(minimal_gedcom)

        assert gedcom.header is not None
        assert gedcom.header.source is not None
        assert gedcom.header.gedcom_version.version == "5.5.1"
        assert gedcom.header.charset == "UTF-8"


class TestRecordCounts:
    """Tests for correct record counts."""

    def test_individual_count(self, family_with_members):
        """Count individuals correctly."""
        gedcom = parse_string(family_with_members)
        assert len(gedcom.individuals) == 4

    def test_family_count(self, family_with_members):
        """Count families correctly."""
        gedcom = parse_string(family_with_members)
        assert len(gedcom.families) == 1

    def test_source_count(self, source_with_citations):
        """Count sources correctly."""
        gedcom = parse_string(source_with_citations)
        assert len(gedcom.sources) == 1

    def test_repository_count(self, source_with_citations):
        """Count repositories correctly."""
        gedcom = parse_string(source_with_citations)
        assert len(gedcom.repositories) == 1

    def test_media_count(self, media_objects_gedcom):
        """Count media objects correctly."""
        gedcom = parse_string(media_objects_gedcom)
        assert len(gedcom.media_objects) == 1


class TestComplexGedcom:
    """Tests for complex GEDCOM with multiple record types."""

    def test_all_record_types(self):
        """Parse file with all record types."""
        gedcom_str = """\
0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Smith/
1 BIRT
2 DATE 4 Jun 1982
1 FAMS @F1@
0 @I2@ INDI
1 NAME Jane /Doe/
1 FAMS @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 15 Jun 2010
2 SOUR @S1@
0 @S1@ SOUR
1 TITL Marriage Records
1 REPO @R1@
0 @R1@ REPO
1 NAME Local Archives
0 @O1@ OBJE
1 FILE photo.jpg
2 FORM jpg
0 TRLR
"""
        gedcom = parse_string(gedcom_str)

        assert len(gedcom.individuals) == 2
        assert len(gedcom.families) == 1
        assert len(gedcom.sources) == 1
        assert len(gedcom.repositories) == 1
        assert len(gedcom.media_objects) == 1

    def test_references_resolved(self):
        """All references should be resolved after parsing."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 FAMS @F1@
1 SOUR @S1@
0 @I2@ INDI
1 NAME Jane /Doe/
1 FAMS @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 @S1@ SOUR
1 TITL Test Source
1 REPO @R1@
0 @R1@ REPO
1 NAME Test Repo
0 TRLR
"""
        gedcom = parse_string(gedcom_str)

        # Individual -> Family resolved
        john = gedcom.get_individual("@I1@")
        assert john.spouse_families[0].family is not None

        # Individual -> Source resolved
        assert john.sources[0].source is not None

        # Family -> Individual resolved
        fam = gedcom.get_family("@F1@")
        assert fam.get_spouse_by_role("HUSB").individual is not None

        # Source -> Repository resolved
        src = gedcom.get_source("@S1@")
        assert src.repository is not None


class TestGedcomStats:
    """Tests for GEDCOM stats property."""

    def test_stats_individuals(self, family_with_members):
        """Stats should include individual count."""
        gedcom = parse_string(family_with_members)
        assert gedcom.stats["individuals"] == 4

    def test_stats_families(self, family_with_members):
        """Stats should include family count."""
        gedcom = parse_string(family_with_members)
        assert gedcom.stats["families"] == 1

    def test_stats_sources(self, source_with_citations):
        """Stats should include source count."""
        gedcom = parse_string(source_with_citations)
        assert gedcom.stats["sources"] == 1


class TestHeaderParsing:
    """Tests for GEDCOM header parsing."""

    def test_header_source_name(self, ancestry_quirks_gedcom):
        """Parse header source name."""
        gedcom = parse_string(ancestry_quirks_gedcom)

        assert gedcom.header.source is not None
        # system_id contains the source name from the SOUR tag value
        assert gedcom.header.source.system_id == "Ancestry.com Family Trees"

    def test_header_source_product_name(self, ancestry_quirks_gedcom):
        """Parse header source product name."""
        gedcom = parse_string(ancestry_quirks_gedcom)

        # NAME tag under SOUR contains the product name
        assert gedcom.header.source.name == "Ancestry.com Member Trees"

    def test_header_gedcom_version(self, minimal_gedcom):
        """Parse GEDCOM version."""
        gedcom = parse_string(minimal_gedcom)

        assert gedcom.header.gedcom_version.version == "5.5.1"
        assert gedcom.header.gedcom_version.form == "LINEAGE-LINKED"
