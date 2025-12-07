"""GEDCOM date model with parsing support.

Handles various date formats found in GEDCOM files, including Ancestry.com quirks
like year ranges and slash-formatted dates.

GEDCOM 5.5.1: DATE_VALUE
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#DATE_VALUE
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum

from pydantic import Field

from .base import GedcomBaseModel


class DateModifier(str, Enum):
    """GEDCOM date modifiers indicating precision or range.

    GEDCOM 5.5.1: DATE_APPROXIMATED, DATE_RANGE, DATE_PERIOD
    """

    EXACT = "EXACT"
    ABOUT = "ABT"
    CALCULATED = "CAL"
    ESTIMATED = "EST"
    BEFORE = "BEF"
    AFTER = "AFT"
    BETWEEN = "BET"
    FROM = "FROM"
    TO = "TO"


# Month name mappings
MONTH_MAP: dict[str, int] = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

# Regex patterns for date parsing
STANDARD_DATE_PATTERN = re.compile(r"^(?P<day>\d{1,2})?\s*(?P<month>[A-Za-z]{3})?\s*(?P<year>\d{4})$")
SLASH_DATE_PATTERN = re.compile(r"^(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})$")
YEAR_RANGE_PATTERN = re.compile(r"^(?P<year_start>\d{4})-(?P<year_end>\d{4})$")
MODIFIER_PATTERN = re.compile(
    r"^(?P<modifier>ABT\.?|CAL\.?|EST\.?|BEF\.?|AFT\.?|ABOUT|BEFORE|AFTER)\s+",
    re.IGNORECASE,
)
BETWEEN_PATTERN = re.compile(
    r"^BET\.?\s+(.+?)\s+AND\s+(.+)$",
    re.IGNORECASE,
)


class GedcomDate(GedcomBaseModel):
    """Represents a GEDCOM date with original text and parsed components.

    GEDCOM 5.5.1: DATE_VALUE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#DATE_VALUE

    Supports various formats:
    - Standard: "4 Jun 1982", "Jun 1982", "1982"
    - Slash format: "05/28/1960" (Ancestry quirk)
    - Year range: "2010-2019" (Ancestry quirk)
    - Approximate: "Abt. 1817", "About 1934"
    - Before/After: "Bef. 1877", "Aft. 1845"
    - Between: "BET 1792 AND 1793"

    Attributes:
        original: Original date string from GEDCOM file. GEDCOM tag: DATE
        modifier: Date precision modifier (ABT, BEF, AFT, etc.).
        year: Parsed year component.
        month: Parsed month component (1-12).
        day: Parsed day component (1-31).
        year_end: End year for ranges (e.g., "2010-2019" or BET...AND).
        month_end: End month for ranges.
        day_end: End day for ranges.
        date_value: Python date object if fully parseable.
        date_end_value: Python date object for range end if parseable.
        is_parsed: Whether parsing was successful.
    """

    original: str = Field(
        ...,
        description="Original date text from GEDCOM. GEDCOM tag: DATE",
    )
    modifier: DateModifier | None = Field(
        None,
        description="Date precision modifier (ABT, BEF, AFT, etc.).",
    )
    year: int | None = Field(None, description="Parsed year component.")
    month: int | None = Field(None, description="Parsed month (1-12).")
    day: int | None = Field(None, description="Parsed day (1-31).")
    year_end: int | None = Field(None, description="End year for date ranges.")
    month_end: int | None = Field(None, description="End month for date ranges.")
    day_end: int | None = Field(None, description="End day for date ranges.")
    date_value: date | None = Field(
        None,
        description="Python date object if fully parseable.",
    )
    date_end_value: date | None = Field(
        None,
        description="Python date for range end if parseable.",
    )
    is_parsed: bool = Field(
        False,
        description="Whether date parsing extracted any components.",
    )

    @classmethod
    def from_string(cls, date_str: str) -> GedcomDate:
        """Parse a GEDCOM date string into components.

        Args:
            date_str: The raw date string from a GEDCOM file.

        Returns:
            GedcomDate with original text preserved and components parsed
            on a best-effort basis.
        """
        original = date_str.strip()
        working = original
        modifier: DateModifier | None = None
        year: int | None = None
        month: int | None = None
        day: int | None = None
        year_end: int | None = None
        month_end: int | None = None
        day_end: int | None = None
        date_value: date | None = None
        date_end_value: date | None = None

        # Check for BETWEEN...AND pattern first
        between_match = BETWEEN_PATTERN.match(working)
        if between_match:
            modifier = DateModifier.BETWEEN
            start_str = between_match.group(1).strip()
            end_str = between_match.group(2).strip()

            # Parse start date
            start_parts = _parse_date_parts(start_str)
            year, month, day = start_parts

            # Parse end date
            end_parts = _parse_date_parts(end_str)
            year_end, month_end, day_end = end_parts
        else:
            # Check for modifier prefix
            mod_match = MODIFIER_PATTERN.match(working)
            if mod_match:
                mod_text = mod_match.group("modifier").upper().rstrip(".")
                modifier = _map_modifier(mod_text)
                working = working[mod_match.end() :].strip()

            # Check for year range (Ancestry quirk: "2010-2019")
            range_match = YEAR_RANGE_PATTERN.match(working)
            if range_match:
                year = int(range_match.group("year_start"))
                year_end = int(range_match.group("year_end"))
                if modifier is None:
                    modifier = DateModifier.BETWEEN
            else:
                # Parse as standard date
                year, month, day = _parse_date_parts(working)

        # Build date objects if we have enough components
        if year and month and day:
            try:
                date_value = date(year, month, day)
            except ValueError:
                pass

        if year_end and month_end and day_end:
            try:
                date_end_value = date(year_end, month_end, day_end)
            except ValueError:
                pass

        is_parsed = year is not None

        return cls(
            original=original,
            modifier=modifier,
            year=year,
            month=month,
            day=day,
            year_end=year_end,
            month_end=month_end,
            day_end=day_end,
            date_value=date_value,
            date_end_value=date_end_value,
            is_parsed=is_parsed,
        )

    def __str__(self) -> str:
        """Return the original date string."""
        return self.original


def _parse_date_parts(date_str: str) -> tuple[int | None, int | None, int | None]:
    """Parse a date string into year, month, day components.

    Args:
        date_str: Date string without modifiers.

    Returns:
        Tuple of (year, month, day), any of which may be None.
    """
    date_str = date_str.strip()

    # Try slash format first (MM/DD/YYYY)
    slash_match = SLASH_DATE_PATTERN.match(date_str)
    if slash_match:
        return (
            int(slash_match.group("year")),
            int(slash_match.group("month")),
            int(slash_match.group("day")),
        )

    # Try standard GEDCOM format (DD MMM YYYY or MMM YYYY or YYYY)
    standard_match = STANDARD_DATE_PATTERN.match(date_str)
    if standard_match:
        year = int(standard_match.group("year")) if standard_match.group("year") else None
        month_str = standard_match.group("month")
        month = MONTH_MAP.get(month_str.upper()) if month_str else None
        day = int(standard_match.group("day")) if standard_match.group("day") else None
        return (year, month, day)

    # Try year only
    if date_str.isdigit() and len(date_str) == 4:
        return (int(date_str), None, None)

    return (None, None, None)


def _map_modifier(mod_text: str) -> DateModifier:
    """Map modifier text to DateModifier enum."""
    mapping = {
        "ABT": DateModifier.ABOUT,
        "ABOUT": DateModifier.ABOUT,
        "CAL": DateModifier.CALCULATED,
        "EST": DateModifier.ESTIMATED,
        "BEF": DateModifier.BEFORE,
        "BEFORE": DateModifier.BEFORE,
        "AFT": DateModifier.AFTER,
        "AFTER": DateModifier.AFTER,
    }
    return mapping.get(mod_text, DateModifier.ABOUT)
