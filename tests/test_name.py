"""Tests for GEDCOM name parsing."""

from pygedreader.models import Name


class TestNameParsing:
    """Tests for Name.from_string parsing."""

    def test_standard_name(self):
        """Parse standard GEDCOM name format."""
        n = Name.from_string("John /Smith/")
        assert n.full == "John /Smith/"
        assert n.first_name == "John"
        assert n.surname == "Smith"

    def test_given_name_only(self):
        """Parse name with given name only."""
        n = Name.from_string("John //")
        assert n.first_name == "John"
        assert n.surname is None

    def test_surname_only(self):
        """Parse name with surname only."""
        n = Name.from_string("/Smith/")
        assert n.first_name is None
        assert n.surname == "Smith"

    def test_multiple_given_names(self):
        """Parse name with multiple given names."""
        n = Name.from_string("John Robert /Smith/")
        assert n.first_name == "John Robert"
        assert n.surname == "Smith"

    def test_suffix_after_surname(self):
        """Parse name with suffix after surname."""
        n = Name.from_string("John /Smith/ Jr.")
        assert n.full == "John /Smith/ Jr."
        assert n.first_name == "John"
        assert n.surname == "Smith"
        # Note: suffix parsing would need explicit NSFX tag

    def test_no_slashes(self):
        """Handle name without slashes."""
        n = Name.from_string("John Smith")
        assert n.full == "John Smith"
        # Without slashes, can't reliably parse components
        assert n.first_name is None
        assert n.surname is None

    def test_empty_name(self):
        """Handle empty name."""
        n = Name.from_string("")
        assert n.full == ""
        assert n.first_name is None
        assert n.surname is None


class TestNameDisplayName:
    """Tests for Name.display_name method."""

    def test_display_name_both_parts(self):
        """Display name with both first and surname."""
        n = Name.from_string("John /Smith/")
        assert n.display_name() == "John Smith"

    def test_display_name_first_only(self):
        """Display name with first name only."""
        n = Name.from_string("John //")
        assert n.display_name() == "John"

    def test_display_name_surname_only(self):
        """Display name with surname only."""
        n = Name.from_string("/Smith/")
        assert n.display_name() == "Smith"

    def test_display_name_fallback(self):
        """Display name falls back to full string."""
        n = Name.from_string("Unknown Person")
        assert n.display_name() == "Unknown Person"

    def test_str_returns_display_name(self):
        """String representation should use display_name."""
        n = Name.from_string("John /Smith/")
        assert str(n) == "John Smith"
