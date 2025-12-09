"""Tests for GEDCOM place parsing."""

from pygedreader.models import Place


class TestPlaceParsing:
    """Tests for Place.from_string parsing."""

    def test_four_part_place(self):
        """Parse full four-part place: City, County, State, Country."""
        p = Place.from_string("New Haven, New Haven, Connecticut, USA")
        assert p.name == "New Haven, New Haven, Connecticut, USA"
        assert p.city == "New Haven"
        assert p.county == "New Haven"
        assert p.state == "Connecticut"
        assert p.country == "USA"

    def test_three_part_place(self):
        """Parse three-part place: City, State, Country."""
        p = Place.from_string("Boston, Massachusetts, USA")
        assert p.city == "Boston"
        assert p.county is None
        assert p.state == "Massachusetts"
        assert p.country == "USA"

    def test_two_part_place(self):
        """Parse two-part place: City, Country."""
        p = Place.from_string("London, England")
        assert p.city == "London"
        assert p.country == "England"

    def test_single_part_place(self):
        """Parse single-part place."""
        p = Place.from_string("USA")
        assert p.city == "USA"
        assert p.country is None

    def test_extra_parts_ignored(self):
        """Extra parts beyond four are ignored."""
        p = Place.from_string("A, B, C, D, E, F")
        assert p.city == "A"
        assert p.county == "B"
        assert p.state == "C"
        assert p.country == "D"

    def test_whitespace_stripped(self):
        """Whitespace around parts should be stripped."""
        p = Place.from_string("  New York  ,  New York  ,  USA  ")
        assert p.city == "New York"
        assert p.state == "New York"
        assert p.country == "USA"

    def test_empty_parts_skipped(self):
        """Empty parts (consecutive commas) should be skipped."""
        p = Place.from_string("Boston,, USA")
        assert p.city == "Boston"
        assert p.country == "USA"

    def test_str_returns_name(self):
        """String representation should return full name."""
        p = Place.from_string("Boston, Massachusetts, USA")
        assert str(p) == "Boston, Massachusetts, USA"
