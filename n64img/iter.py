from itertools import zip_longest
from math import ceil
from typing import Iterable, Tuple


WORD_SIZE = 4  # bytes


def iter_image_indexes(
    width: int,
    height: int,
    bytes_per_pixel: float = 1,
    flip_h: bool = False,
    flip_v: bool = False,
    swap_words: bool = False,
) -> Iterable[Tuple[int, int, int]]:
    w = int(width * bytes_per_pixel)
    h = int(height * 1)

    xrange = (
        range(w - ceil(bytes_per_pixel), -1, -ceil(bytes_per_pixel))
        if flip_h
        else range(0, w, ceil(bytes_per_pixel))
    )

    if swap_words:
        xrange = list(xrange)
        xrange_swapped = []
        pixels_per_word = ceil(WORD_SIZE / bytes_per_pixel)
        for i in range(0, len(xrange), pixels_per_word * 2):
            xrange_swapped += [
                *xrange[i + pixels_per_word : i + pixels_per_word + pixels_per_word],
                *xrange[i : i + pixels_per_word],
            ]

    yrange = range(h - 1, -1, -1) if flip_v else range(0, h, 1)

    for i, y in enumerate(yrange):
        for x in xrange_swapped if (swap_words and i % 2 == 1) else xrange:
            yield x, y, (y * w) + x
