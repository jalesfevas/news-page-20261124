#!/usr/bin/env python3
"""Copy the make.fun entry image into an output directory and report its identity.

The source image is validated before anything is written: PNG signature,
size ceiling, and IHDR dimensions must all match.
"""

import hashlib
import os
import shutil
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(REPO_DIR, "entry.png")


def fail(message):
    sys.stderr.write("error: %s\n" % message)
    sys.exit(1)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def validate(path):
    """Return (size, width, height) or exit with a clear message."""
    if not os.path.isfile(path):
        fail("source image not found: %s" % path)

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        fail("source image is %d bytes, limit is %d bytes" % (size, MAX_BYTES))

    with open(path, "rb") as handle:
        header = handle.read(24)

    if len(header) < 24:
        fail("source image is only %d bytes, too short to hold a PNG header" % size)

    if header[:8] != PNG_SIGNATURE:
        fail(
            "source image does not begin with the 8-byte PNG signature "
            "(got %s)" % header[:8].hex()
        )

    if header[12:16] != b"IHDR":
        fail(
            "first chunk is not IHDR (got %r)" % header[12:16]
        )

    width, height = struct.unpack(">II", header[16:24])
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        fail(
            "IHDR dimensions are %dx%d, expected %dx%d"
            % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT)
        )

    return size, width, height


def main():
    size, width, height = validate(SOURCE)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, destination)

    print("source     : %s" % SOURCE)
    print("size       : %d bytes" % size)
    print("dimensions : %dx%d" % (width, height))
    print("sha256     : %s" % sha256_of(SOURCE))
    print("copy       : %s" % destination)


if __name__ == "__main__":
    main()
