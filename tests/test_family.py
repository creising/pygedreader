"""Tests for GEDCOM family parsing."""

from parser import parse_string


class TestFamilyBasics:
    """Tests for basic family parsing."""

    def test_parse_family(self, family_with_members):
        """Parse family record."""
        gedcom = parse_string(family_with_members)
        assert len(gedcom.families) == 1

        fam = gedcom.get_family("@F1@")
        assert fam is not None
        assert fam.xref == "@F1@"

    def test_family_spouses(self, family_with_members):
        """Parse HUSB and WIFE as spouses."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        assert len(fam.spouses) == 2
        xrefs = [s.xref for s in fam.spouses]
        assert "@I1@" in xrefs
        assert "@I2@" in xrefs

    def test_spouse_roles_preserved(self, family_with_members):
        """Original HUSB/WIFE roles should be preserved."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        husb = fam.get_spouse_by_role("HUSB")
        assert husb is not None
        assert husb.xref == "@I1@"

        wife = fam.get_spouse_by_role("WIFE")
        assert wife is not None
        assert wife.xref == "@I2@"

    def test_family_children(self, family_with_members):
        """Parse CHIL as children."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        assert len(fam.children) == 2
        xrefs = [c.xref for c in fam.children]
        assert "@I3@" in xrefs
        assert "@I4@" in xrefs

    def test_spouse_xrefs_property(self, family_with_members):
        """Test spouse_xrefs property."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        xrefs = fam.spouse_xrefs
        assert "@I1@" in xrefs
        assert "@I2@" in xrefs

    def test_child_xrefs_property(self, family_with_members):
        """Test child_xrefs property."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        xrefs = fam.child_xrefs
        assert "@I3@" in xrefs
        assert "@I4@" in xrefs


class TestFamilyEvents:
    """Tests for family events."""

    def test_marriage_event(self, family_with_members):
        """Parse marriage event with date and place."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        assert fam.marriage is not None
        assert fam.marriage.date is not None
        assert fam.marriage.date.year == 1990
        assert fam.marriage.date.month == 6
        assert fam.marriage.date.day == 15
        assert fam.marriage.place is not None
        assert fam.marriage.place.city == "Boston"

    def test_divorce_event(self):
        """Parse divorce event."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 DIV
2 DATE 5 May 2000
0 @I1@ INDI
1 NAME John //
0 @I2@ INDI
1 NAME Jane //
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        fam = gedcom.get_family("@F1@")

        assert fam.divorce is not None
        assert fam.divorce.date is not None
        assert fam.divorce.date.year == 2000


class TestFamilyReferences:
    """Tests for family reference resolution."""

    def test_spouse_references_resolved(self, family_with_members):
        """Spouse references should resolve to Individual objects."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        for spouse in fam.spouses:
            assert spouse.individual is not None
            assert spouse.individual.xref == spouse.xref

    def test_child_references_resolved(self, family_with_members):
        """Child references should resolve to Individual objects."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        for child in fam.children:
            assert child.individual is not None
            assert child.individual.xref == child.xref

    def test_spouse_resolved_has_name(self, family_with_members):
        """Resolved spouse should have name data."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        husb = fam.get_spouse_by_role("HUSB")
        assert husb.individual.primary_name.first_name == "John"

        wife = fam.get_spouse_by_role("WIFE")
        assert wife.individual.primary_name.first_name == "Jane"

    def test_child_resolved_has_name(self, family_with_members):
        """Resolved child should have name data."""
        gedcom = parse_string(family_with_members)
        fam = gedcom.get_family("@F1@")

        child_names = [c.individual.primary_name.first_name for c in fam.children]
        assert "Johnny" in child_names
        assert "Jenny" in child_names
