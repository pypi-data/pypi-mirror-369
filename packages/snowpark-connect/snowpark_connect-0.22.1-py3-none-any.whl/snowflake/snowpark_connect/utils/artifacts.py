#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import gzip
import os
import pathlib
import tempfile
import zlib

from snowflake import snowpark


def check_checksum(data: bytes, crc: int) -> bool:
    return zlib.crc32(data) != crc


def write_artifact(
    session: snowpark.Session, name: str, data: bytes, overwrite: bool = False
) -> str:
    # When using the notebook we have greatly limited disk space (around 1GB), so the provided artifacts cannot be too large.
    # When name starts with "cache/" it indicates that the provided artifact should be compressed to save space on the disk.
    if name.startswith("cache/"):
        filename = name + ".gz"
    elif name.startswith("archives/"):
        filename = name + ".archive"
    else:
        filename = name
    return write_temporary_artifact(session, filename, data, overwrite)


def write_temporary_artifact(
    session: snowpark.Session, name: str, data: bytes, overwrite: bool
) -> str:
    # We write to /tmp (or windows equivalent) to keep the data in memory.
    # This is designed to work in TCM as well.
    if os.name != "nt":
        filepath = f"/tmp/sas-{session.session_id}/{name}"
    else:
        filepath = f"{tempfile.gettempdir()}/sas-{session.session_id}/{name}"
    # The name comes to us as a path (e.g. cache/<name>), so we need to create
    # the parent directory if it doesn't exist to avoid errors during writing.
    pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    write_mode = "wb" if overwrite else "ab"
    open_file = gzip.open if name.startswith("cache/") else open
    with open_file(filepath, write_mode) as in_memory_file:
        in_memory_file.write(data)
    return filepath
