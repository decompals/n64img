from math import ceil
from pathlib import Path

import png

from n64img import iter
from n64img.color import unpack_color


class Image:
    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height
        self.greyscale = False
        self.alpha = False
        self.flip_h = False
        self.flip_v = False
        self.palette = None

    def __str__(self):
        return "Image(width={}, height={}, data={})".format(
            self.width, self.height, self.data
        )

    def get_writer(self) -> png.Writer:
        return png.Writer(
            self.width,
            self.height,
            greyscale=self.greyscale,
            alpha=self.alpha,
            palette=self.palette,
        )

    def parse(self) -> bytes:
        if not self.flip_h and not self.flip_v:
            return self.data

        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 1, 1, self.flip_h, self.flip_v
        ):
            img.append(self.data[i])

        return bytes(img)

    def write(self, outpath: Path):
        with open(outpath, "wb") as f:
            pixels = self.parse()
            self.get_writer().write_array(f, pixels)

    def size(self) -> int:
        return self.width * self.height


class CI4(Image):
    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 0.5, 1, self.flip_h, self.flip_v
        ):
            img.append(self.data[i] >> 4)
            img.append(self.data[i] & 0xF)

        return bytes(img)

    def size(self) -> int:
        return self.width * self.height // 2


class CI8(Image):
    pass


class I4(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 0.5, 1, self.flip_h, self.flip_v
        ):
            b = self.data[i]

            i1 = (b >> 4) & 0xF
            i2 = b & 0xF

            i1 = ceil(0xFF * (i1 / 15))
            i2 = ceil(0xFF * (i2 / 15))

            img += bytes((i1, i2))

        return bytes(img)

    def size(self) -> int:
        return self.width * self.height // 2


class I8(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True


class IA4(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True
        self.alpha = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 0.5, 1, flip_h=self.flip_h, flip_v=self.flip_v
        ):
            b = self.data[i]

            h = (b >> 4) & 0xF
            l = b & 0xF

            i1 = (h >> 1) & 0xF
            a1 = (h & 1) * 0xFF
            i1 = ceil(0xFF * (i1 / 7))

            i2 = (l >> 1) & 0xF
            a2 = (l & 1) * 0xFF
            i2 = ceil(0xFF * (i2 / 7))

            img += bytes((i1, a1, i2, a2))

        return bytes(img)

    def size(self) -> int:
        return self.width * self.height // 2


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

            i = ceil(0xFF * (i / 15))
            a = ceil(0xFF * (a / 15))

            img += bytes((i, a))

        return bytes(img)


class IA16(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = True
        self.alpha = True

    def size(self) -> int:
        return self.width * self.height * 2


class RGBA16(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = False
        self.alpha = True

    def parse(self) -> bytes:
        img = bytearray()

        for x, y, i in iter.iter_image_indexes(
            self.width, self.height, 2, 1, self.flip_h, self.flip_v
        ):
            img += bytes(unpack_color(self.data[i:]))

        return bytes(img)

    def size(self) -> int:
        return self.width * self.height * 2


class RGBA32(Image):
    def __init__(self, data, width, height):
        super().__init__(data, width, height)
        self.greyscale = False
        self.alpha = True

    def size(self) -> int:
        return self.width * self.height * 4
