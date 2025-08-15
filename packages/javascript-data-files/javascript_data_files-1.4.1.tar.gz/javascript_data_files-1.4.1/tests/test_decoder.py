"""
Tests for `javascript_data_files.decoder`.
"""

import pytest

from javascript_data_files.decoder import decode_from_json


@pytest.mark.parametrize(
    "json_string",
    [
        '{ "sides": 3, "sides": 4 }',
        '{ "sides": 3, "colour": "blue", "sides": 4 }',
        '[{ "nested": { "sides": 3, "sides": 4 } }]',
    ],
)
def test_object_with_duplicate_names_is_rejected(json_string: str) -> None:
    """
    Trying to decode a JavaScript string which includes an object
    with duplicate names throws a ValueError.
    """
    with pytest.raises(ValueError, match="Found duplicate name in JSON object: sides"):
        decode_from_json(json_string)


def test_object_with_multiple_duplicate_names_is_rejected() -> None:
    """
    Trying to decode a JavaScript string which includes an object
    with multiple duplicate names throws a ValueError.
    """
    with pytest.raises(ValueError, match="Found duplicate names in JSON object:"):
        decode_from_json(
            '{ "sides": 3, "colour": "blue", "sides": 4, "colour": "red" }'
        )
