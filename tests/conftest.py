"""Shared test fixtures for PyGEDCOM tests."""

import pytest


@pytest.fixture
def minimal_gedcom() -> str:
    """Minimal valid GEDCOM file."""
    return """\
0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Smith/
0 TRLR
"""


@pytest.fixture
def individual_with_events() -> str:
    """Individual with birth, death, and residence events."""
    return """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
2 GIVN John
2 SURN Smith
1 SEX M
1 BIRT
2 DATE 4 Jun 1982
2 PLAC New Haven, New Haven, Connecticut, USA
1 DEAT
2 DATE 15 Mar 2020
2 PLAC Boston, Massachusetts, USA
1 RESI
2 DATE 2010-2019
2 PLAC New York, New York, USA
0 TRLR
"""


@pytest.fixture
def ancestry_quirks_gedcom() -> str:
    """GEDCOM with Ancestry.com-specific quirks."""
    return """\
0 HEAD
1 SOUR Ancestry.com Family Trees
2 NAME Ancestry.com Member Trees
2 _TREE Test Family Tree
3 RIN 12345
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
2 SOUR @S1@
3 _APID 1,1234::5678
1 MARR
2 DATE 14 Nov 1981
2 PLAC Hartford, Connecticut, USA
1 _MILT
2 DATE 1944
2 PLAC Fort Benning, Georgia, USA
0 @S1@ SOUR
1 TITL U.S. Census Records
1 AUTH Ancestry.com
1 _APID 1,1234::0
0 TRLR
"""


@pytest.fixture
def family_with_members() -> str:
    """Family with spouses and children."""
    return """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
1 FAMS @F1@
0 @I2@ INDI
1 NAME Jane /Doe/
1 SEX F
1 FAMS @F1@
0 @I3@ INDI
1 NAME Johnny /Smith/
1 SEX M
1 FAMC @F1@
0 @I4@ INDI
1 NAME Jenny /Smith/
1 SEX F
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 CHIL @I4@
1 MARR
2 DATE 15 Jun 1990
2 PLAC Boston, Massachusetts, USA
0 TRLR
"""


@pytest.fixture
def source_with_citations() -> str:
    """Source record with inline citations."""
    return """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @I1@ INDI
1 NAME John /Smith/
1 BIRT
2 DATE 4 Jun 1982
2 SOUR @S1@
3 PAGE Page 123, Line 45
3 DATA
4 WWW https://example.com/record/123
3 _APID 1,5678::9012
1 SOUR @S1@
2 PAGE General reference
2 _APID 1,5678::0
0 @S1@ SOUR
1 TITL U.S. Census Records, 1900
1 AUTH U.S. Census Bureau
1 PUBL Ancestry.com
2 DATE 2010
2 PLAC Provo, UT, USA
1 REPO @R1@
0 @R1@ REPO
1 NAME Ancestry.com
0 TRLR
"""


@pytest.fixture
def media_objects_gedcom() -> str:
    """GEDCOM with media objects."""
    return """\
0 HEAD
1 GEDC
2 VERS 5.5.1
0 @O1@ OBJE
1 FILE
2 FORM jpg
3 TYPE image
3 _MTYPE document
3 _SIZE 196382
3 _WDTH 2070
3 _HGHT 1730
2 TITL Wedding Photo
1 DATE 15 Jun 1990
1 _OID abc123-def456
0 TRLR
"""
