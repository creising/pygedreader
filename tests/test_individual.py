"""Tests for GEDCOM individual parsing."""

from parser import parse_string


class TestIndividualBasics:
    """Tests for basic individual parsing."""

    def test_minimal_individual(self, minimal_gedcom):
        """Parse minimal individual with just name."""
        gedcom = parse_string(minimal_gedcom)
        assert len(gedcom.individuals) == 1

        indi = gedcom.get_individual("@I1@")
        assert indi is not None
        assert indi.xref == "@I1@"
        assert len(indi.names) == 1
        assert indi.names[0].surname == "Smith"
        assert indi.names[0].first_name == "John"

    def test_individual_with_sex(self, individual_with_events):
        """Parse individual with sex."""
        gedcom = parse_string(individual_with_events)
        indi = gedcom.get_individual("@I1@")
        assert indi.sex == "M"

    def test_primary_name_property(self, minimal_gedcom):
        """Test primary_name property returns first name."""
        gedcom = parse_string(minimal_gedcom)
        indi = gedcom.get_individual("@I1@")
        assert indi.primary_name is not None
        assert indi.primary_name.first_name == "John"

    def test_display_name_property(self, minimal_gedcom):
        """Test display_name property."""
        gedcom = parse_string(minimal_gedcom)
        indi = gedcom.get_individual("@I1@")
        assert indi.display_name == "John Smith"


class TestIndividualEvents:
    """Tests for individual events."""

    def test_birth_event(self, individual_with_events):
        """Parse birth event with date and place."""
        gedcom = parse_string(individual_with_events)
        indi = gedcom.get_individual("@I1@")

        assert indi.birth is not None
        assert indi.birth.date is not None
        assert indi.birth.date.year == 1982
        assert indi.birth.date.month == 6
        assert indi.birth.date.day == 4
        assert indi.birth.place is not None
        assert indi.birth.place.city == "New Haven"
        assert indi.birth.place.state == "Connecticut"

    def test_death_event(self, individual_with_events):
        """Parse death event with date and place."""
        gedcom = parse_string(individual_with_events)
        indi = gedcom.get_individual("@I1@")

        assert indi.death is not None
        assert indi.death.date is not None
        assert indi.death.date.year == 2020
        assert indi.death.date.month == 3
        assert indi.death.date.day == 15
        assert indi.death.place is not None
        assert indi.death.place.city == "Boston"

    def test_residence_event(self, individual_with_events):
        """Parse residence event."""
        gedcom = parse_string(individual_with_events)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.residences) == 1
        resi = indi.residences[0]
        assert resi.date is not None
        # Year range format
        assert resi.date.year == 2010
        assert resi.date.year_end == 2019
        assert resi.place is not None
        assert resi.place.city == "New York"

    def test_get_all_events(self, individual_with_events):
        """Test get_all_events returns all events."""
        gedcom = parse_string(individual_with_events)
        indi = gedcom.get_individual("@I1@")

        events = indi.get_all_events()
        # Birth + Death + 1 Residence = 3 events
        assert len(events) == 3


class TestAncestryQuirks:
    """Tests for Ancestry.com-specific quirks."""

    def test_marr_under_indi(self, ancestry_quirks_gedcom):
        """Parse MARR event under INDI (Ancestry quirk)."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.marriages) == 1
        marr = indi.marriages[0]
        assert marr.date is not None
        assert marr.date.year == 1981
        assert marr.date.month == 11
        assert marr.date.day == 14
        assert marr.place is not None
        assert marr.place.city == "Hartford"

    def test_sex_with_source(self, ancestry_quirks_gedcom):
        """Parse SEX tag with nested SOUR (Ancestry quirk)."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        assert indi.sex == "M"
        assert len(indi.sex_sources) == 1
        assert indi.sex_sources[0].xref == "@S1@"

    def test_custom_milt_event(self, ancestry_quirks_gedcom):
        """Parse _MILT (military) custom event."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.custom_events) == 1
        milt = indi.custom_events[0]
        # Custom events use .tag (not .event_type which is only for standard events)
        assert milt.tag == "_MILT"
        assert milt.date is not None
        assert milt.date.year == 1944
        assert milt.place is not None
        assert milt.place.city == "Fort Benning"

    def test_apid_on_sex_source(self, ancestry_quirks_gedcom):
        """Parse _APID custom tag on source citation."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.sex_sources) == 1
        src = indi.sex_sources[0]
        assert "_APID" in src.custom_tags
        # Custom tags are stored as lists
        assert "1,1234::5678" in src.custom_tags["_APID"]


class TestFamilyLinks:
    """Tests for family links (FAMC/FAMS)."""

    def test_spouse_family_link(self, family_with_members):
        """Parse FAMS link."""
        gedcom = parse_string(family_with_members)

        father = gedcom.get_individual("@I1@")
        assert len(father.spouse_families) == 1
        assert father.spouse_families[0].xref == "@F1@"

        mother = gedcom.get_individual("@I2@")
        assert len(mother.spouse_families) == 1
        assert mother.spouse_families[0].xref == "@F1@"

    def test_parent_family_link(self, family_with_members):
        """Parse FAMC link."""
        gedcom = parse_string(family_with_members)

        child1 = gedcom.get_individual("@I3@")
        assert len(child1.parent_families) == 1
        assert child1.parent_families[0].xref == "@F1@"

        child2 = gedcom.get_individual("@I4@")
        assert len(child2.parent_families) == 1
        assert child2.parent_families[0].xref == "@F1@"

    def test_family_links_resolved(self, family_with_members):
        """Family links should be resolved to actual Family objects."""
        gedcom = parse_string(family_with_members)

        father = gedcom.get_individual("@I1@")
        assert father.spouse_families[0].family is not None
        assert father.spouse_families[0].family.xref == "@F1@"

        child = gedcom.get_individual("@I3@")
        assert child.parent_families[0].family is not None
        assert child.parent_families[0].family.xref == "@F1@"
