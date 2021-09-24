# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '15 Jul 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import pytest

from item_generator.extraction_methods import postprocessors


@pytest.fixture
def fpath():
    return 'a/b/c/d.txt'


@pytest.fixture
def source_dict():
    return {
        'date': '2021-05-02'
    }


@pytest.fixture
def isodate_processor():
    return postprocessors.ISODateProcessor(date_keys=['date'])

@pytest.fixture
def isodate_processor_with_format():
    return postprocessors.ISODateProcessor(date_keys=['date'], format='%Y%m')

@pytest.fixture
def facet_map_processor():
    return postprocessors.FacetMapProcessor(term_map={'date': 'start_date'})


@pytest.fixture
def bbox_processor():
    return postprocessors.BBOXProcessor(key_list=['west', 'south', 'east', 'north'])


def test_isodate_processor(isodate_processor, fpath, source_dict):
    """Check isodate processor does what's expected"""
    expected = source_dict.copy()
    expected['date'] = '2021-05-02T00:00:00'

    output = isodate_processor.run(fpath, source_dict=source_dict)
    assert output == expected


def test_isodate_processor_bad_date(isodate_processor, fpath, caplog):
    """Check isodate processor does what's expected.date

    Conditions:
        - No format string
        - Date string not parsable by dateutil

    Expected:
        - Produce an error
        - Delete the date key
    """
    source_dict = {
        'date': '202105'
    }
    expected = {}

    output = isodate_processor.run(fpath, source_dict=source_dict)
    assert output == expected
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'ERROR'


def test_isodate_processor_with_good_format(isodate_processor_with_format, fpath):
    """Check isodate processor.
    Conditions:
        - Format string does match date string
        - Date string not parsable by dateutil

    Expected:
        - Successfully use strptime to parse the date
    """

    source_dict = {
        'date': '202105'
    }
    expected = source_dict.copy()
    expected['date'] = '2021-05-01T00:00:00'

    output = isodate_processor_with_format.run(fpath, source_dict=source_dict)
    assert output == expected


def test_isodate_processor_with_bad_format(isodate_processor_with_format, fpath, caplog):
    """Check isodate processor.
    Conditions:
        - Format string does not match date string
        - Date string parsable by dateutil

    Expected:
        - Produce warning
        - Successfully Use dateutil to parse the date
    """
    source_dict = {
        'date': '20210501'
    }
    expected = source_dict.copy()
    expected['date'] = '2021-05-01T00:00:00'

    output = isodate_processor_with_format.run(fpath, source_dict=source_dict)
    assert output == expected
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'WARNING'


def test_isodate_processor_with_bad_format_bad_dateutil(isodate_processor_with_format, fpath, caplog):
    """Check isodate processor.
    Conditions:
        - Format string does not match date string
        - Date string ambiguous and nor parsable by dateutil

    Expected:
        Should delete the date
    """
    source_dict = {
        'date': '2021010101'
    }
    expected = {}

    output = isodate_processor_with_format.run(fpath, source_dict=source_dict)
    assert output == expected
    assert len(caplog.records) == 2


def test_facet_map_processor(facet_map_processor, fpath, source_dict):
    """
    Check processor changes name of named facets
    """
    expected = {
        'start_date': source_dict['date']
    }

    output = facet_map_processor.run(fpath, source_dict=source_dict)
    assert output == expected


def test_bbox_processor(bbox_processor, fpath):
    source_dict = {
        'north': '42.0',
        'south': '38.0',
        'east': '-28.0',
        'west': '-37.0'
    }

    expected = [
        float(source_dict['west']),
        float(source_dict['south']),
        float(source_dict['east']),
        float(source_dict['north'])
    ]

    output = bbox_processor.run(fpath, source_dict=source_dict)
    assert output == expected
