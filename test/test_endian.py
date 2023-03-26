import unittest

from n64img.image import (
    CI4,
    I4,
    IA4,
)


class TestEndian(unittest.TestCase):
    def create_4bpp_image(self, t, w, h):
        data = bytearray((w * h) >> 1)
        for i in range(0, len(data)):
            data[i] = i & 0xFF

        return t(data, w, h)

    def test_ci4_endian_big(self):
        img = self.create_4bpp_image(CI4, 4, 4)
        pixels = img.parse()
        self.assertEqual(bytearray([
            0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03,
            0x00, 0x04, 0x00, 0x05, 0x00, 0x06, 0x00, 0x07,
        ]), pixels)

    def test_i4_endian_big(self):
        img = self.create_4bpp_image(I4, 4, 4)
        pixels = img.parse()
        print("*****")
        print(pixels)
        print("*****")
        self.assertEqual(bytearray([
            0x00, 0x00, 0x00, 0x11, 0x00, 0x22, 0x00, 0x33,
            0x00, 0x44, 0x00, 0x55, 0x00, 0x66, 0x00, 0x77,
        ]), pixels)

    def test_ia4_endian_big(self):
        img = self.create_4bpp_image(IA4, 4, 4)
        pixels = img.parse()
        print("*****")
        print(pixels)
        print("*****")
        self.assertEqual(bytearray([
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0xFF,
            0x00, 0x00, 0x24, 0x00,
            0x00, 0x00, 0x24, 0xFF,
            0x00, 0x00, 0x49, 0x00,
            0x00, 0x00, 0x49, 0xFF,
            0x00, 0x00, 0x6D, 0x00,
            0x00, 0x00, 0x6D, 0xFF,
        ]), pixels)
