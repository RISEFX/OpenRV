#
# Copyright Contributors to the OpenRV Project
#
# SPDX-License-Identifier: Apache-2.0
#

"""Smoke test for RV's OpenImageIO Python module.

Writes and reads tif/png/jpg/exr, and checks that OIIO's colorconvert matches a
PyOpenColorIO CPU processor. Run it with RV's interpreter, for example:

    QT_QPA_PLATFORM=minimal <RV>/bin/py-interp oiio_python_smoke.py [<RV>]

With <RV> given, both modules must load from below it. Exits non-zero on any failure.
"""

import os
import sys
import tempfile
import traceback

FORMATS = ("tif", "png", "jpg", "exr")
SIZE = 64
RGB = (0.5, 0.2, 0.1)
# 8-bit formats and JPEG compression change the value slightly.
READ_TOLERANCE = 0.02
OCIO_CONFIG = "ocio://cg-config-v1.0.0_aces-v1.3_ocio-v2.1"
OCIO_SRC = "ACEScg"
OCIO_DST = "sRGB - Texture"
OCIO_TOLERANCE = 1e-5


def check_write_read(oiio, directory):
    buf = oiio.ImageBuf(oiio.ImageSpec(SIZE, SIZE, 3, oiio.FLOAT))
    oiio.ImageBufAlgo.fill(buf, RGB)
    for ext in FORMATS:
        path = os.path.join(directory, "smoke." + ext)
        if not buf.write(path):
            raise RuntimeError(f"writing {ext} failed: {buf.geterror()}")
        image = oiio.ImageInput.open(path)
        if not image:
            raise RuntimeError(f"opening {ext} failed: {oiio.geterror()}")
        pixels = image.read_image("float")
        image.close()
        if pixels is None or pixels.shape != (SIZE, SIZE, 3):
            raise RuntimeError(f"reading {ext} failed: {oiio.geterror()}")
        diff = max(abs(float(a) - b) for a, b in zip(pixels[0, 0], RGB))
        if diff > READ_TOLERANCE:
            raise RuntimeError(f"{ext} pixel {tuple(pixels[0, 0])} differs from {RGB}")
        print(f"{ext}: written and read", flush=True)


def check_ocio(oiio, ocio):
    src = oiio.ImageBuf(oiio.ImageSpec(1, 1, 3, oiio.FLOAT))
    oiio.ImageBufAlgo.fill(src, RGB)
    dst = oiio.ImageBufAlgo.colorconvert(
        src, OCIO_SRC, OCIO_DST, colorconfig=OCIO_CONFIG
    )
    if dst.has_error:
        raise RuntimeError(f"colorconvert failed: {dst.geterror()}")
    oiio_px = dst.getpixel(0, 0)

    config = ocio.Config.CreateFromFile(OCIO_CONFIG)
    processor = config.getProcessor(OCIO_SRC, OCIO_DST)
    ocio_px = processor.getDefaultCPUProcessor().applyRGB(list(RGB))

    diff = max(abs(a - b) for a, b in zip(oiio_px, ocio_px))
    print(f"colorconvert: oiio {oiio_px}, ocio {tuple(ocio_px)}, max diff {diff}")
    # An unchanged pixel means OIIO skipped the conversion.
    if oiio_px == RGB or diff > OCIO_TOLERANCE:
        raise RuntimeError("OIIO colorconvert does not match PyOpenColorIO")


def check_location(module, root):
    path = os.path.realpath(module.__file__)
    root = os.path.realpath(root)
    if os.path.commonpath([path, root]) != root:
        raise RuntimeError(f"{module.__name__} loaded from outside {root}: {path}")


def main(root):
    import OpenImageIO as oiio
    import PyOpenColorIO as ocio

    print("OpenImageIO", oiio.VERSION_STRING, oiio.__file__)
    print("PyOpenColorIO", ocio.__version__, ocio.__file__)
    if root:
        check_location(oiio, root)
        check_location(ocio, root)
    print("OIIO libraries:", oiio.get_string_attribute("library_list"), flush=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        check_write_read(oiio, directory)
    check_ocio(oiio, ocio)


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else None)
        print("OK", flush=True)
        code = 0
    except Exception:
        traceback.print_exc()
        print("FAILED", flush=True)
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    # Exit without teardown, so the script also ends `rv -pyeval`, which does not quit by itself.
    os._exit(code)
