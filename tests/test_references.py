"""Tests for GEDCOM cross-reference resolution."""

from parser import parse_string


class TestIndividualToFamilyRefs:
    """Tests for Individual -> Family reference resolution."""

    def test_fams_resolves_to_family(self, family_with_members):
        """FAMS reference should resolve to Family object."""
        gedcom = parse_string(family_with_members)
        father = gedcom.get_individual("@I1@")

        assert len(father.spouse_families) == 1
        link = father.spouse_families[0]
        assert link.family is not None
        assert link.family.xref == "@F1@"

    def test_famc_resolves_to_family(self, family_with_members):
        """FAMC reference should resolve to Family object."""
        gedcom = parse_string(family_with_members)
        child = gedcom.get_individual("@I3@")

        assert len(child.parent_families) == 1
        link = child.parent_families[0]
        assert link.family is not None
        assert link.family.xref == "@F1@"


class TestFamilyToIndividualRefs:
    """Tests for Family -> Individual reference resolution."""

    def test_husb_resolves_to_individual(self, family_with_members):
        """HUSB reference should resolve to Individual object."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        husb = fam.get_spouse_by_role("HUSB")
        assert husb is not None
        assert husb.individual is not None
        assert husb.individual.xref == "@I1@"
        assert husb.individual.primary_name.first_name == "John"

    def test_wife_resolves_to_individual(self, family_with_members):
        """WIFE reference should resolve to Individual object."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        wife = fam.get_spouse_by_role("WIFE")
        assert wife is not None
        assert wife.individual is not None
        assert wife.individual.xref == "@I2@"
        assert wife.individual.primary_name.first_name == "Jane"

    def test_chil_resolves_to_individual(self, family_with_members):
        """CHIL reference should resolve to Individual object."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        assert len(fam.children) == 2
        for child_link in fam.children:
            assert child_link.individual is not None
            assert child_link.individual.xref in ["@I3@", "@I4@"]


class TestSourceReferences:
    """Tests for source reference resolution."""

    def test_citation_resolves_to_source(self, source_with_citations):
        """Source citation should resolve to Source object."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.sources) == 1
        citation = indi.sources[0]
        assert citation.source is not None
        assert citation.source.xref == "@S1@"
        assert citation.source.title == "U.S. Census Records, 1900"

    def test_event_citation_resolves(self, source_with_citations):
        """Event-level source citation should resolve."""
        gedcom = parse_string(source_with_citations)
        indi = gedcom.get_individual("@I1@")

        assert indi.birth is not None
        assert len(indi.birth.sources) == 1
        citation = indi.birth.sources[0]
        assert citation.source is not None
        assert citation.source.title == "U.S. Census Records, 1900"


class TestRepositoryReferences:
    """Tests for source -> repository reference resolution."""

    def test_source_repo_resolves(self, source_with_citations):
        """Source REPO reference should resolve to Repository."""
        gedcom = parse_string(source_with_citations)
        src = gedcom.get_source("@S1@")

        assert src.repository_xref == "@R1@"
        assert src.repository is not None
        assert src.repository.xref == "@R1@"
        assert src.repository.name == "Ancestry.com"


class TestMissingReferences:
    """Tests for handling missing/invalid references."""

    def test_missing_family_ref_is_none(self):
        """Missing family reference should resolve to None."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 FAMS @F999@
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.spouse_families) == 1
        assert indi.spouse_families[0].xref == "@F999@"
        assert indi.spouse_families[0].family is None  # Not resolved

    def test_missing_individual_ref_is_none(self):
        """Missing individual reference should resolve to None."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @F1@ FAM
1 HUSB @I999@
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        fam = gedcom.get_family("@F1@")

        assert len(fam.spouses) == 1
        assert fam.spouses[0].xref == "@I999@"
        assert fam.spouses[0].individual is None  # Not resolved

    def test_missing_source_ref_is_none(self):
        """Missing source reference should resolve to None."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 SOUR @S999@
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.sources) == 1
        assert indi.sources[0].xref == "@S999@"
        assert indi.sources[0].source is None  # Not resolved


class TestBidirectionalReferences:
    """Tests for bidirectional reference consistency."""

    def test_family_and_individual_consistent(self, family_with_members):
        """Family and Individual refs should point to each other."""
        gedcom = parse_string(family_with_members)

        # Get family
        fam = gedcom.get_family("@F1@")

        # Get father through family
        husb = fam.get_spouse_by_role("HUSB")
        father = husb.individual

        # Father's spouse_families should link back to same family
        assert len(father.spouse_families) == 1
        assert father.spouse_families[0].family is fam

    def test_parent_child_bidirectional(self, family_with_members):
        """Parent-child refs should be bidirectional."""
        gedcom = parse_string(family_with_members)

        # Get child
        child = gedcom.get_individual("@I3@")

        # Child's parent family
        parent_fam = child.parent_families[0].family

        # Parent family should contain this child
        child_xrefs = [c.xref for c in parent_fam.children]
        assert child.xref in child_xrefs
