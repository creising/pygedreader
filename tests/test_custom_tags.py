"""Tests for GEDCOM custom tag handling."""

from parser import parse_string


class TestCustomTagsOnRecords:
    """Tests for custom tags on various records."""

    def test_apid_on_source(self, ancestry_quirks_gedcom):
        """Parse _APID on source record."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        src = gedcom.get_source("@S1@")

        assert "_APID" in src.custom_tags
        # Custom tags are stored as lists to support multiple values
        assert "1,1234::0" in src.custom_tags["_APID"]

    def test_apid_on_citation(self, ancestry_quirks_gedcom):
        """Parse _APID on source citation."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        # Citation on SEX
        assert len(indi.sex_sources) == 1
        citation = indi.sex_sources[0]
        assert "_APID" in citation.custom_tags
        assert "1,1234::5678" in citation.custom_tags["_APID"]

    def test_tree_on_header(self, ancestry_quirks_gedcom):
        """Parse _TREE custom tag on header source."""
        gedcom = parse_string(ancestry_quirks_gedcom)

        # _TREE is nested under SOUR in header
        assert gedcom.header is not None
        assert gedcom.header.source is not None
        assert "_TREE" in gedcom.header.source.custom_tags

    def test_oid_on_media(self, media_objects_gedcom):
        """Parse _OID on media object."""
        gedcom = parse_string(media_objects_gedcom)
        assert len(gedcom.media_objects) == 1

        media = gedcom.get_media("@O1@")
        assert media is not None
        assert "_OID" in media.custom_tags
        assert "abc123-def456" in media.custom_tags["_OID"]


class TestCustomEvents:
    """Tests for custom event types."""

    def test_milt_event_tag(self, ancestry_quirks_gedcom):
        """Parse _MILT custom event tag is preserved."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        assert len(indi.custom_events) == 1
        milt = indi.custom_events[0]
        # Custom events use .tag (not .event_type which is only for standard events)
        assert milt.tag == "_MILT"

    def test_milt_event_has_date(self, ancestry_quirks_gedcom):
        """Custom _MILT event has date parsed."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        milt = indi.custom_events[0]
        assert milt.date is not None
        assert milt.date.year == 1944

    def test_milt_event_has_place(self, ancestry_quirks_gedcom):
        """Custom _MILT event has place parsed."""
        gedcom = parse_string(ancestry_quirks_gedcom)
        indi = gedcom.get_individual("@I1@")

        milt = indi.custom_events[0]
        assert milt.place is not None
        assert milt.place.city == "Fort Benning"
        assert milt.place.state == "Georgia"


class TestMediaCustomTags:
    """Tests for custom tags on media objects."""

    def test_media_mtype(self, media_objects_gedcom):
        """Parse _MTYPE custom tag on media file."""
        gedcom = parse_string(media_objects_gedcom)
        media = gedcom.get_media("@O1@")

        # Media has single .file (not .files)
        assert media.file is not None
        assert "_MTYPE" in media.file.custom_tags
        assert "document" in media.file.custom_tags["_MTYPE"]

    def test_media_size_tags(self, media_objects_gedcom):
        """Parse _SIZE, _WDTH, _HGHT custom tags."""
        gedcom = parse_string(media_objects_gedcom)
        media = gedcom.get_media("@O1@")

        assert media.file is not None
        assert "_SIZE" in media.file.custom_tags
        assert "196382" in media.file.custom_tags["_SIZE"]
        assert "_WDTH" in media.file.custom_tags
        assert "2070" in media.file.custom_tags["_WDTH"]
        assert "_HGHT" in media.file.custom_tags
        assert "1730" in media.file.custom_tags["_HGHT"]


class TestCustomTagPreservation:
    """Tests that custom tags are preserved but don't break parsing."""

    def test_unknown_custom_tag_preserved(self):
        """Unknown custom tags should be preserved in custom_tags dict."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 _CUSTOM This is a custom value
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        indi = gedcom.get_individual("@I1@")

        assert "_CUSTOM" in indi.custom_tags
        assert "This is a custom value" in indi.custom_tags["_CUSTOM"]

    def test_multiple_custom_tags(self):
        """Multiple custom tags should all be preserved."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 _TAG1 Value1
1 _TAG2 Value2
1 _TAG3 Value3
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        indi = gedcom.get_individual("@I1@")

        assert "_TAG1" in indi.custom_tags
        assert "_TAG2" in indi.custom_tags
        assert "_TAG3" in indi.custom_tags

    def test_custom_tag_doesnt_break_standard_parsing(self):
        """Custom tags shouldn't interfere with standard field parsing."""
        gedcom_str = """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 _BEFORE Before birth
1 BIRT
2 DATE 4 Jun 1982
1 _AFTER After birth
0 TRLR
"""
        gedcom = parse_string(gedcom_str)
        indi = gedcom.get_individual("@I1@")

        # Standard fields still parsed correctly
        assert indi.names[0].first_name == "John"
        assert indi.birth is not None
        assert indi.birth.date.year == 1982

        # Custom tags preserved
        assert "_BEFORE" in indi.custom_tags
        assert "_AFTER" in indi.custom_tags
