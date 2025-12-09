"""Base classes for GEDCOM models.

This module provides the foundation classes that all GEDCOM models inherit from,
including common configuration and the custom_tags storage mechanism.

GEDCOM 5.5.1: LINEAGE-LINKED GEDCOM
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Type alias for cross-references (e.g., "@I123@", "@F456@")
XRef = str


class GedcomBaseModel(BaseModel):
    """Base model for all GEDCOM structures.

    All GEDCOM models inherit from this class to get consistent configuration
    and the custom_tags dictionary for storing non-standard tags.

    Attributes:
        custom_tags: Storage for custom underscore-prefixed tags (e.g., _APID, _MILT).
            Keys are tag names, values are lists of parsed values or nested structures.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    custom_tags: dict[str, list[Any]] = Field(
        default_factory=dict,
        description="Custom underscore-prefixed tags not in the standard spec.",
    )


class GedcomRecord(GedcomBaseModel):
    """Base class for top-level GEDCOM records with an identifier.

    Top-level records (INDI, FAM, SOUR, REPO, OBJE, SUBM) have a unique
    cross-reference identifier in the format @XREF@.

    GEDCOM 5.5.1: RECORD
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#record

    Attributes:
        xref: Unique identifier for this record (e.g., "@I123@", "@F456@").
            GEDCOM tag: The tag appears as "0 @XREF@ TAG".
    """

    xref: str = Field(
        ...,
        description="Unique record identifier. GEDCOM format: @XREF@",
        pattern=r"^@[A-Za-z0-9_]+@$",
    )
