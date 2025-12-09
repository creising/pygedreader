"""Tests for GEDCOM date parsing."""

from datetime import date

from pygedreader.models import DateModifier, GedcomDate


class TestStandardDateFormats:
    """Tests for standard GEDCOM date formats."""

    def test_full_date(self):
        """Parse full date: day month year."""
        d = GedcomDate.from_string("4 Jun 1982")
        assert d.original == "4 Jun 1982"
        assert d.year == 1982
        assert d.month == 6
        assert d.day == 4
        assert d.is_parsed is True
        assert d.date_value == date(1982, 6, 4)

    def test_month_and_year(self):
        """Parse month and year only."""
        d = GedcomDate.from_string("Jun 1982")
        assert d.year == 1982
        assert d.month == 6
        assert d.day is None
        assert d.is_parsed is True
        assert d.date_value is None  # Can't create date without day

    def test_year_only(self):
        """Parse year only."""
        d = GedcomDate.from_string("1982")
        assert d.year == 1982
        assert d.month is None
        assert d.day is None
        assert d.is_parsed is True

    def test_two_digit_day(self):
        """Parse date with two-digit day."""
        d = GedcomDate.from_string("15 Mar 2020")
        assert d.day == 15
        assert d.month == 3
        assert d.year == 2020


class TestDateModifiers:
    """Tests for date modifiers (ABT, BEF, AFT, etc.)."""

    def test_about(self):
        """Parse ABT modifier."""
        d = GedcomDate.from_string("ABT 1817")
        assert d.modifier == DateModifier.ABOUT
        assert d.year == 1817

    def test_about_with_period(self):
        """Parse Abt. with trailing period (Ancestry format)."""
        d = GedcomDate.from_string("Abt. 1817")
        assert d.modifier == DateModifier.ABOUT
        assert d.year == 1817

    def test_before(self):
        """Parse BEF modifier."""
        d = GedcomDate.from_string("BEF 1877")
        assert d.modifier == DateModifier.BEFORE
        assert d.year == 1877

    def test_after(self):
        """Parse AFT modifier."""
        d = GedcomDate.from_string("AFT 1845")
        assert d.modifier == DateModifier.AFTER
        assert d.year == 1845

    def test_between(self):
        """Parse BET...AND range."""
        d = GedcomDate.from_string("BET 1792 AND 1793")
        assert d.modifier == DateModifier.BETWEEN
        assert d.year == 1792
        assert d.year_end == 1793

    def test_modifier_case_insensitive(self):
        """Modifiers should be case insensitive."""
        d1 = GedcomDate.from_string("abt 1900")
        d2 = GedcomDate.from_string("ABT 1900")
        assert d1.modifier == d2.modifier == DateModifier.ABOUT


class TestAncestryDateQuirks:
    """Tests for Ancestry.com-specific date formats."""

    def test_slash_format(self):
        """Parse MM/DD/YYYY format."""
        d = GedcomDate.from_string("05/28/1960")
        assert d.month == 5
        assert d.day == 28
        assert d.year == 1960
        assert d.is_parsed is True

    def test_year_range(self):
        """Parse year range format (YYYY-YYYY)."""
        d = GedcomDate.from_string("2010-2019")
        assert d.year == 2010
        assert d.year_end == 2019
        assert d.modifier == DateModifier.BETWEEN

    def test_original_preserved(self):
        """Original date string should always be preserved."""
        d = GedcomDate.from_string("sometime in 1800s")
        assert d.original == "sometime in 1800s"
        # May or may not parse, but original is always there


class TestDateEdgeCases:
    """Tests for edge cases and unusual dates."""

    def test_empty_string(self):
        """Handle empty string."""
        d = GedcomDate.from_string("")
        assert d.original == ""
        assert d.is_parsed is False

    def test_whitespace_only(self):
        """Handle whitespace-only string."""
        d = GedcomDate.from_string("   ")
        assert d.original == ""
        assert d.is_parsed is False

    def test_str_returns_original(self):
        """String representation should return original."""
        d = GedcomDate.from_string("4 Jun 1982")
        assert str(d) == "4 Jun 1982"
