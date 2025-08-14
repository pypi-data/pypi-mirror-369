import re


def str_to_enum(
    str_enum_class,
    str_value: str,
    ignore_not_found: bool = False,
    enum_default=None,
):
    for key, member in str_enum_class.__members__.items():
        if str_value == member.value:
            return member
    if ignore_not_found:
        return enum_default
    raise ValueError(f"Invalid enum value: {str_value}")


def contains_versioned_url(url: str) -> bool:
    """
    Check if the URL contains a versioned path like /v1/ or /v2/, etc.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL contains /v1/, /v2/, etc., otherwise False.
    """
    return re.search(r"/v\d+", url) is not None
