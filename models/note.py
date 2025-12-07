"""GEDCOM note model.

Represents notes which may contain structured key-value data in Ancestry exports.

GEDCOM 5.5.1: NOTE_STRUCTURE
https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#NOTE_STRUCTURE
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import GedcomBaseModel, XRef


class Note(GedcomBaseModel):
    """Represents a note attached to a record or event.

    GEDCOM 5.5.1: NOTE_STRUCTURE
    https://gedcom.io/specifications/FamilySearchGEDCOMv7.html#NOTE_STRUCTURE

    Ancestry exports often embed structured data in notes, such as:
    "Occupation: Employee; Marital Status: Married"

    This model preserves the original text and attempts to parse
    key-value pairs from structured notes.

    Attributes:
        text: Full note text content. GEDCOM tag: NOTE
        parsed_data: Key-value pairs extracted from structured notes.
        xref: Reference to a standalone NOTE record (rare in Ancestry exports).
    """

    text: str = Field(
        ...,
        description="Full note text content. GEDCOM tag: NOTE",
    )
    parsed_data: dict[str, str] = Field(
        default_factory=dict,
        description="Key-value pairs extracted from structured notes.",
    )
    xref: Optional[XRef] = Field(
        None,
        description="Reference to standalone NOTE record. GEDCOM format: @N123@",
    )

    @classmethod
    def from_string(cls, note_str: str, xref: Optional[XRef] = None) -> Note:
        """Parse a note string, extracting key-value pairs if structured.

        Looks for patterns like "Key: Value" or "Key: Value; Key2: Value2"
        commonly found in Ancestry census notes.

        Args:
            note_str: The raw note text from a GEDCOM file.
            xref: Optional reference to a standalone NOTE record.

        Returns:
            Note with text preserved and any key-value pairs extracted
            into parsed_data.
        """
        text = note_str.strip()
        parsed_data: dict[str, str] = {}

        # Try to extract key-value pairs if the note looks structured
        if ":" in text:
            # Split by semicolon for multiple pairs
            segments = text.split(";") if ";" in text else [text]

            for segment in segments:
                segment = segment.strip()
                if ":" in segment:
                    # Split on first colon only
                    key, _, value = segment.partition(":")
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        parsed_data[key] = value

        return cls(
            text=text,
            parsed_data=parsed_data,
            xref=xref,
        )

    def __str__(self) -> str:
        """Return the note text."""
        return self.text
