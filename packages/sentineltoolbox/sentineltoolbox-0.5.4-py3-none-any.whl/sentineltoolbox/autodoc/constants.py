import enum

from sentineltoolbox.typedefs import fix_enum


class DisplayMode(enum.Enum):
    text = "Raw Text"
    rich = "Rich Text"
    dev = "For developers"


def to_display_mode(data: str | int | DisplayMode) -> DisplayMode:
    """
    Converts input data to a `DisplayMode` enumeration member using the generic `to_enum` function.

    Parameters:
        data (str | int | DisplayMode): The value to convert. It can be:
            - An instance of `DisplayMode`
            - The value of a `DisplayMode` member (name, value, or index)

    Returns:
        DisplayMode: The matching `DisplayMode` member, or `DisplayMode.text` as a default.
    """
    return fix_enum(data, DisplayMode, DisplayMode.text)
