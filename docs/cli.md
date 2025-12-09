# CLI Reference

pygedreader includes a command-line tool for quick file inspection and JSON export.

## Installation

The CLI is included when you install pygedreader:

```bash
pip install pygedreader
```

## Commands

### `info` - Show File Statistics

Display a summary of a GEDCOM file:

```bash
pygedreader info family-tree.ged
```

Output:

```
File: family-tree.ged

Header:
  Source: Ancestry.com Family Trees
  GEDCOM: 5.5.1
  Charset: UTF-8

Records:
  Individuals: 253
  Families: 99
  Sources: 81
  Media Objects: 54

Events:
  Individuals with birth: 218
  MARR under INDI (Ancestry quirk): 55
  Custom events (_MILT, etc.): 2
```

### `parse` - Export to JSON

Export the parsed GEDCOM to JSON:

```bash
# Output to stdout
pygedreader parse family-tree.ged

# Output to file
pygedreader parse family-tree.ged -o output.json

# Compact JSON (no indentation)
pygedreader parse family-tree.ged --indent 0 -o output.json

# Custom indentation
pygedreader parse family-tree.ged --indent 4 -o output.json
```

## Options

| Option | Description |
|--------|-------------|
| `-o`, `--output` | Output file path (default: stdout) |
| `--indent` | JSON indentation level (default: 2, use 0 for compact) |
| `--encoding` | Input file encoding (default: utf-8) |

## Examples

Check what's in a file before processing:

```bash
pygedreader info ~/Downloads/ancestry-export.ged
```

Export for use with other tools:

```bash
pygedreader parse family-tree.ged -o data.json
```

Pipe to jq for quick queries:

```bash
pygedreader parse family-tree.ged | jq '.individuals | length'
```
