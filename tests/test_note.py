"""Tests for GEDCOM note parsing."""

from pygedreader.models import Note


class TestNoteParsing:
    """Tests for Note.from_string parsing."""

    def test_plain_text_note(self):
        """Parse plain text note."""
        n = Note.from_string("This is a simple note.")
        assert n.text == "This is a simple note."
        assert n.parsed_data == {}

    def test_structured_single_field(self):
        """Parse structured note with single field."""
        n = Note.from_string("Occupation: Farmer")
        assert n.text == "Occupation: Farmer"
        assert n.parsed_data == {"Occupation": "Farmer"}

    def test_structured_multiple_fields(self):
        """Parse structured note with multiple fields."""
        n = Note.from_string("Occupation: Farmer; Marital Status: Married")
        assert n.parsed_data["Occupation"] == "Farmer"
        assert n.parsed_data["Marital Status"] == "Married"

    def test_structured_with_spaces(self):
        """Parse structured note with spaces around delimiters."""
        n = Note.from_string("Occupation : Employee ; Status : Active")
        assert n.parsed_data["Occupation"] == "Employee"
        assert n.parsed_data["Status"] == "Active"

    def test_colon_in_value(self):
        """Handle colon in value (only first colon is delimiter)."""
        n = Note.from_string("Time: 10:30 AM")
        assert n.parsed_data["Time"] == "10:30 AM"

    def test_note_with_xref(self):
        """Note can have xref to standalone NOTE record."""
        n = Note.from_string("Referenced note", xref="@N1@")
        assert n.text == "Referenced note"
        assert n.xref == "@N1@"

    def test_empty_note(self):
        """Handle empty note."""
        n = Note.from_string("")
        assert n.text == ""
        assert n.parsed_data == {}

    def test_str_returns_text(self):
        """String representation should return text."""
        n = Note.from_string("Test note")
        assert str(n) == "Test note"


class TestAncestryNotes:
    """Tests for Ancestry-specific note patterns."""

    def test_census_occupation_note(self):
        """Parse census occupation note."""
        n = Note.from_string("Occupation: Upholsterer")
        assert n.parsed_data["Occupation"] == "Upholsterer"

    def test_census_relation_note(self):
        """Parse census relation note."""
        n = Note.from_string("Relation to Head: Self; Relative Relation to Head: Wife")
        assert n.parsed_data["Relation to Head"] == "Self"
        assert n.parsed_data["Relative Relation to Head"] == "Wife"

    def test_census_full_note(self):
        """Parse full census note with multiple fields."""
        text = "Occupation: Carpenter; Relation to Head of House: Head; Marital Status: Married"
        n = Note.from_string(text)
        assert n.parsed_data["Occupation"] == "Carpenter"
        assert n.parsed_data["Relation to Head of House"] == "Head"
        assert n.parsed_data["Marital Status"] == "Married"
