from math import ceil
from pathlib import Path
from typing import List, Optional, Tuple

import png

from n64img import iter

Palette = List[Tuple[int, int, int, int]]


class Image:
    def __init__(self, data: bytes, width: int, height: int):
        self.data: bytes = data
        self.width: int = width
        self.height: int = height
        self.depth: int = 1
        self.greyscale: bool = False
        self.alpha: bool = False
        self.flip_h: bool = False
        self.flip_v: bool = False
        self.palette: Optional[Palette] = None

    def __str__(self):
        return "Image(width={}, height={}, data={})".format(
            self.width, self.height, self.data
        )

    def get_writer(self) -> png.Writer:
        return png.Writer(
            self.width,
            self.height,
            greyscale=self.greyscale,  # type: ignore
            alpha=self.alpha,
            palette=self.palette,
        )

    def parse(self) -> bytes:
        if not self.flip_h and not self.flip_v:
            return self.data

        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 1, self.flip_h, self.flip_v
        ):
            img.append(self.data[i])

        return bytes(img)

    def write(self, outpath: Path):
        with open(outpath, "wb") as f:
            pixels = self.parse()
            self.get_writer().write_array(f, pixels)

    def mipmap_size(self) -> int:
        size = 0
        width = self.width
        while width > 0:
            # NOTE: rows must be padded to 8-byte boundary
            row = height = width
            remainder = ceil(width * self.depth) % 8
            if remainder != 0:
                row += ceil((8 - remainder) / self.depth)
            size += row * height * self.depth
            width >>= 1
        return size

    def size(self) -> int:
        return ceil(self.width * self.height * self.depth)


class CI4(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 0.5

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, self.depth, self.flip_h, self.flip_v
        ):
            img.append(self.data[i] >> 4)
            img.append(self.data[i] & 0xF)

        return bytes(img)


class CI8(Image):
    pass


# I1, a very primitive type where each bit represents one pixel.
# Generally, only used for debug fonts and rendered using the cpu instead of the rdp.
class I1(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 0.125
        self.greyscale = True

    def parse(self) -> bytes:
        if self.flip_h:
            raise Exception("I1 images cannot be flipped horizontally.")
        if self.flip_v:
            raise Exception("I1 images cannot be flipped vertically.")

        img = bytearray()

        for b in self.data:
            # iterate over bits
            for j in range(8, 0, -1):
                # Store the value of each bit as a pixel.
                p = (b >> (j - 1)) & 0x1
                # Convert active bits to RGB white and inactive to black.
                p *= 0xFF

                img.append(p)

        return bytes(img)


class I4(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 0.5
        self.greyscale = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, self.depth, self.flip_h, self.flip_v
        ):
            b = self.data[i]

            i1 = (b >> 4) & 0xF
            i2 = b & 0xF

            i1 = (i1 << 4) | i1
            i2 = (i2 << 4) | i2

            img += bytes((i1, i2))

        return bytes(img)


class I8(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True


class IA4(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 0.5
        self.greyscale = True
        self.alpha = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, self.depth, flip_h=self.flip_h, flip_v=self.flip_v
        ):
            b = self.data[i]

            h = (b >> 4) & 0xF
            l = b & 0xF

            i1 = h & 0xE
            i1 = (i1 << 4) | (i1 << 1) | (i1 >> 2)
            a1 = (h & 1) * 0xFF

            i2 = l & 0xE
            i2 = (i2 << 4) | (i2 << 1) | (i2 >> 2)
            a2 = (l & 1) * 0xFF

            img += bytes((i1, a1, i2, a2))

        return bytes(img)


class IA8(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True
        self.alpha = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, flip_h=self.flip_h, flip_v=self.flip_v
        ):
            b = self.data[i]

            i = (b >> 4) & 0xF
            a = b & 0xF

            i = (i << 4) | i
            a = (a << 4) | a

            img += bytes((i, a))

        return bytes(img)


class IA16(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 2
        self.greyscale = True
        self.alpha = True


class RGBA16(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 2
        self.greyscale = False
        self.alpha = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, self.depth, self.flip_h, self.flip_v
        ):
            s = int.from_bytes(self.data[i:i+2], byteorder='big')

            r = (s >> 11) & 0x1F
            g = (s >>  6) & 0x1F
            b = (s >>  1) & 0x1F

            r = (r << 3) | (r >> 2)
            g = (g << 3) | (g >> 2)
            b = (b << 3) | (b >> 2)

            a = 255 * (s & 1)

            img += bytes((r,g,b,a))

        return bytes(img)


class RGBA32(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.depth = 4
        self.greyscale = False
        self.alpha = True
