"""Command-line interface for pygedreader.

Provides commands for parsing GEDCOM files and exporting to various formats.

Usage:
    pygedreader parse family-tree.ged                    # Output JSON to stdout
    pygedreader parse family-tree.ged -o output.json    # Output to file
    pygedreader parse family-tree.ged --format json     # Explicit format
    pygedreader info family-tree.ged                    # Show file statistics
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from models import Gedcom
from parser import parse_file


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command == "parse":
        return cmd_parse(args)
    elif args.command == "info":
        return cmd_info(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="pygedreader",
        description="Parse GEDCOM files and export to various formats.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse a GEDCOM file and export to another format",
    )
    parse_parser.add_argument(
        "input",
        type=Path,
        help="Input GEDCOM file",
    )
    parse_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parse_parser.add_argument(
        "-f", "--format",
        choices=["json"],
        default="json",
        help="Output format (default: json)",
    )
    parse_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation (default: 2, use 0 for compact)",
    )
    parse_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Input file encoding (default: utf-8)",
    )

    # info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show statistics about a GEDCOM file",
    )
    info_parser.add_argument(
        "input",
        type=Path,
        help="Input GEDCOM file",
    )
    info_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Input file encoding (default: utf-8)",
    )

    return parser.parse_args()


def cmd_parse(args: argparse.Namespace) -> int:
    """Handle the parse command."""
    input_path: Path = args.input

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        gedcom = parse_file(input_path, encoding=args.encoding)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        output = gedcom_to_json(gedcom, indent=args.indent if args.indent > 0 else None)
    else:
        print(f"Unsupported format: {args.format}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Handle the info command."""
    input_path: Path = args.input

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        gedcom = parse_file(input_path, encoding=args.encoding)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        return 1

    print(f"File: {input_path}")
    print()

    if gedcom.header:
        print("Header:")
        if gedcom.header.source:
            print(f"  Source: {gedcom.header.source.system_id}")
            if gedcom.header.source.name:
                print(f"  Name: {gedcom.header.source.name}")
            if gedcom.header.source.version:
                print(f"  Version: {gedcom.header.source.version}")
        if gedcom.header.gedcom_version:
            print(f"  GEDCOM: {gedcom.header.gedcom_version.version}")
        print(f"  Charset: {gedcom.header.charset}")
        if gedcom.header.date:
            print(f"  Export Date: {gedcom.header.date.original}")
        print()

    print("Records:")
    stats = gedcom.stats
    print(f"  Individuals: {stats['individuals']}")
    print(f"  Families: {stats['families']}")
    print(f"  Sources: {stats['sources']}")
    print(f"  Repositories: {stats['repositories']}")
    print(f"  Media Objects: {stats['media_objects']}")
    print(f"  Submitters: {stats['submitters']}")
    print()

    # Count some interesting stats
    birth_count = sum(1 for i in gedcom.individuals if i.birth)
    death_count = sum(1 for i in gedcom.individuals if i.death)
    marriage_indi_count = sum(1 for i in gedcom.individuals if i.marriages)
    custom_event_count = sum(len(i.custom_events) for i in gedcom.individuals)

    print("Events:")
    print(f"  Individuals with birth: {birth_count}")
    print(f"  Individuals with death: {death_count}")
    print(f"  Families with marriage: {sum(1 for f in gedcom.families if f.marriage)}")
    if marriage_indi_count:
        print(f"  MARR under INDI (Ancestry quirk): {marriage_indi_count}")
    if custom_event_count:
        print(f"  Custom events (_MILT, etc.): {custom_event_count}")

    return 0


def gedcom_to_json(gedcom: Gedcom, indent: int | None = 2) -> str:
    """Convert a Gedcom object to JSON string.

    Args:
        gedcom: Parsed Gedcom object.
        indent: JSON indentation level (None for compact).

    Returns:
        JSON string representation.
    """
    # Use Pydantic's model_dump for serialization
    data = gedcom.model_dump(
        mode="json",
        exclude_none=True,
        by_alias=False,
    )

    return json.dumps(data, indent=indent, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())
