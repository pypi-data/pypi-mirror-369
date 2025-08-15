# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Various functions to manipulate RGB hex, RGB, HSV and HLS colors."""

import string

RGBColor = tuple[float, float, float]
DEFAULT_COLOR: RGBColor = (0.5, 0.5, 0.5)


def rgb_intensity(rgb: RGBColor):
    """Convert an RGB color to its intensity"""

    return rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114


def contrast_color(rgb: RGBColor) -> str:
    """Return either white or black whichever provides the most contrast"""

    if rgb == (0.0, 0.0, 0.0) or rgb_intensity(rgb) < (160.0 / 255.0):
        return "white"
    else:
        return "black"


def hex_string_to_rgb(value: str, allow_short: bool = True) -> RGBColor:
    """Convert from a hex color string of the form `#abc` or `#abcdef` to an
    RGB tuple.

    :param value: The value to convert
    :type value: str
    :param allow_short: If True then the short of form of an hex value is
                        accepted e.g. #fff
    :type allow_short:  bool
    """
    if value[0] != "#":
        value = f"#{value}"

    for ch in value[1:]:
        if ch not in string.hexdigits:
            return DEFAULT_COLOR

    if len(value) == 7:
        # The following to_iterable function is based on the
        # :func:`grouper` function in the Python standard library docs
        # http://docs.python.org/library/itertools.html
        def to_iterable() -> RGBColor:
            # pylint: disable=missing-docstring
            args = [iter(value[1:])] * 2
            return tuple([int("%s%s" % t, 16) / 255 for t in zip(*args)])[:3]  # type: ignore

    elif len(value) == 4 and allow_short:

        def to_iterable() -> RGBColor:
            # pylint: disable=missing-docstring
            return tuple([int("%s%s" % (t, t), 16) / 255 for t in value[1:]])[:3]  # type: ignore

    else:
        return DEFAULT_COLOR

    try:
        return to_iterable()
    except ValueError:
        return DEFAULT_COLOR
