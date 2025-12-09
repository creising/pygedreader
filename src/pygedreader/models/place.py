"""GEDCOM place model.

Represents geographic locations with optional parsed components.

GEDCOM 5.5.1: PLACE_STRUCTURE
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#PLACE_STRUCTURE
"""

from __future__ import annotations

from pydantic import Field

from .base import GedcomBaseModel


class Place(GedcomBaseModel):
    """Represents a geographic place.

    GEDCOM 5.5.1: PLACE_STRUCTURE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#PLACE_STRUCTURE

    GEDCOM places are typically comma-separated from specific to general:
    "City, County, State, Country"

    Attributes:
        name: Full place name as it appears in the GEDCOM. GEDCOM tag: PLAC
        city: Locality/city component (first part).
        county: County/district component.
        state: State/province component.
        country: Country component (last part).
        latitude: Geographic latitude. GEDCOM tag: LATI (under MAP)
        longitude: Geographic longitude. GEDCOM tag: LONG (under MAP)
    """

    name: str = Field(
        ...,
        description="Full place name. GEDCOM tag: PLAC",
    )
    city: str | None = Field(
        None,
        description="Locality/city (typically first component).",
    )
    county: str | None = Field(
        None,
        description="County/district component.",
    )
    state: str | None = Field(
        None,
        description="State/province component.",
    )
    country: str | None = Field(
        None,
        description="Country (typically last component).",
    )
    latitude: float | None = Field(
        None,
        description="Geographic latitude. GEDCOM tag: LATI",
    )
    longitude: float | None = Field(
        None,
        description="Geographic longitude. GEDCOM tag: LONG",
    )

    @classmethod
    def from_string(cls, place_str: str) -> Place:
        """Parse a place string into components.

        GEDCOM convention is comma-separated, specific to general:
        "City, County, State, Country"

        Args:
            place_str: The raw place string from a GEDCOM file.

        Returns:
            Place with name preserved and components parsed based on
            the number of comma-separated parts.
        """
        name = place_str.strip()
        parts = [p.strip() for p in name.split(",") if p.strip()]

        city: str | None = None
        county: str | None = None
        state: str | None = None
        country: str | None = None

        # Assign based on number of parts
        # Common patterns: "City, State, Country" or "City, County, State, Country"
        if len(parts) == 1:
            # Could be city or country, assume city
            city = parts[0]
        elif len(parts) == 2:
            # City, Country
            city = parts[0]
            country = parts[1]
        elif len(parts) == 3:
            # City, State, Country
            city = parts[0]
            state = parts[1]
            country = parts[2]
        elif len(parts) >= 4:
            # City, County, State, Country (plus any additional)
            city = parts[0]
            county = parts[1]
            state = parts[2]
            country = parts[3]

        return cls(
            name=name,
            city=city,
            county=county,
            state=state,
            country=country,
        )

    def __str__(self) -> str:
        """Return the full place name."""
        return self.name
