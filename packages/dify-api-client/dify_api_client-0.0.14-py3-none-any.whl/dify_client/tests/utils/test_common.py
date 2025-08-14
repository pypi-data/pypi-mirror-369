import pytest

from dify_client.utils._common import contains_versioned_url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://api.example.com/v1", True),
        ("https://api.example.com/V1", False),  # case-insensitive
        ("https://api.example.com/v2/resource", True),
        ("https://api.example.com/v123/resource", True),
        ("https://api.example.com/v/resource", False),
        ("https://api.example.com/resource", False),
    ],
)
def test_contains_versioned_url(url, expected):
    assert contains_versioned_url(url) == expected
