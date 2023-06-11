#! /usr/bin/python3

import argparse
from typing import Optional

from n64img.image import CI4, CI8, I4, I8, IA16, IA4, IA8, RGBA16, RGBA32, Image


def main() -> None:
    SUPPORTED_FORMATS = [
        "ci4",
        "ci8",
        "i4",
        "i8",
        "ia4",
        "ia8",
        "ia16",
        "rgba16",
        "rgba32",
    ]

    parser = argparse.ArgumentParser(description="Create PNGs from data")
    parser.add_argument("in_file")
    parser.add_argument("out_file")
    parser.add_argument("format", choices=SUPPORTED_FORMATS)
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("--palette")
    args = parser.parse_args()

    with open(args.in_file, "rb") as f:
        in_data = f.read()

    palette_data: Optional[bytes] = None
    if args.palette:
        with open(args.palette, "rb") as f:
            palette_data = f.read()

    img: Image
    if args.format == "ci4":
        img = CI4(in_data, args.width, args.height)
    elif args.format == "ci8":
        img = CI8(in_data, args.width, args.height)
    elif args.format == "i4":
        img = I4(in_data, args.width, args.height)
    elif args.format == "i8":
        img = I8(in_data, args.width, args.height)
    elif args.format == "ia4":
        img = IA4(in_data, args.width, args.height)
    elif args.format == "ia8":
        img = IA8(in_data, args.width, args.height)
    elif args.format == "ia16":
        img = IA16(in_data, args.width, args.height)
    elif args.format == "rgba16":
        img = RGBA16(in_data, args.width, args.height)
    elif args.format == "rgba32":
        img = RGBA32(in_data, args.width, args.height)
    else:
        raise ValueError("Invalid format")

    if palette_data:
        img.set_palette(palette_data)

    img.write(args.out_file)


if __name__ == "__main__":
    main()
