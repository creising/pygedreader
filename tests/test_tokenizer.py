"""Tests for GEDCOM line tokenizer."""

from parser.tokenizer import GedcomLine, tokenize_line, tokenize_string


class TestTokenizeLine:
    """Tests for tokenize_line function."""

    def test_parse_record_line(self):
        """Parse a level 0 record line with xref."""
        line = tokenize_line("0 @I1@ INDI", 1)
        assert line is not None
        assert line.level == 0
        assert line.xref == "@I1@"
        assert line.tag == "INDI"
        assert line.value is None

    def test_parse_line_with_value(self):
        """Parse a line with a value."""
        line = tokenize_line("1 NAME John /Smith/", 1)
        assert line is not None
        assert line.level == 1
        assert line.xref is None
        assert line.tag == "NAME"
        assert line.value == "John /Smith/"

    def test_parse_nested_level(self):
        """Parse a deeply nested line."""
        line = tokenize_line("3 _APID 1,1234::5678", 1)
        assert line is not None
        assert line.level == 3
        assert line.tag == "_APID"
        assert line.value == "1,1234::5678"

    def test_parse_tag_only(self):
        """Parse a line with just a tag, no value."""
        line = tokenize_line("1 BIRT", 1)
        assert line is not None
        assert line.level == 1
        assert line.tag == "BIRT"
        assert line.value is None

    def test_empty_line_returns_none(self):
        """Empty lines should return None."""
        assert tokenize_line("", 1) is None
        assert tokenize_line("   ", 1) is None
        assert tokenize_line("\t\t", 1) is None

    def test_handle_bom(self):
        """Handle UTF-8 BOM at start of line."""
        line = tokenize_line("\ufeff0 HEAD", 1)
        assert line is not None
        assert line.level == 0
        assert line.tag == "HEAD"

    def test_normalize_tag_to_uppercase(self):
        """Tags should be normalized to uppercase."""
        line = tokenize_line("1 name John /Smith/", 1)
        assert line is not None
        assert line.tag == "NAME"

    def test_strip_trailing_whitespace(self):
        """Trailing whitespace should be stripped from values."""
        line = tokenize_line("1 NAME John /Smith/   ", 1)
        assert line is not None
        assert line.value == "John /Smith/"

    def test_preserve_line_number(self):
        """Line number should be preserved."""
        line = tokenize_line("0 HEAD", 42)
        assert line is not None
        assert line.line_number == 42


class TestGedcomLineProperties:
    """Tests for GedcomLine properties."""

    def test_is_record_start(self):
        """Test is_record_start property."""
        record_line = tokenize_line("0 @I1@ INDI", 1)
        assert record_line.is_record_start is True

        header_line = tokenize_line("0 HEAD", 1)
        assert header_line.is_record_start is False

        nested_line = tokenize_line("1 NAME John", 1)
        assert nested_line.is_record_start is False

    def test_is_custom_tag(self):
        """Test is_custom_tag property."""
        custom = tokenize_line("1 _MILT", 1)
        assert custom.is_custom_tag is True

        standard = tokenize_line("1 BIRT", 1)
        assert standard.is_custom_tag is False


class TestTokenizeString:
    """Tests for tokenize_string function."""

    def test_tokenize_multiple_lines(self):
        """Tokenize multiple lines from a string."""
        content = """\
0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Smith/
0 TRLR
"""
        tokens = list(tokenize_string(content))
        assert len(tokens) == 5
        assert tokens[0].tag == "HEAD"
        assert tokens[1].tag == "SOUR"
        assert tokens[2].tag == "INDI"
        assert tokens[3].tag == "NAME"
        assert tokens[4].tag == "TRLR"

    def test_skip_empty_lines(self):
        """Empty lines should be skipped."""
        content = """\
0 HEAD

1 SOUR Test

0 TRLR
"""
        tokens = list(tokenize_string(content))
        assert len(tokens) == 3
