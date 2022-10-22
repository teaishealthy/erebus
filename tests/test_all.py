import zlib
from pathlib import Path

import pytest

from erebus import deobfuscate
from erebus.deobfuscator.unwrapper import unwrap

examples_dir = Path(__file__).parent / "examples"


@pytest.fixture
def code():
    return examples_dir.joinpath("obfuscated.py").read_text()


def test_full(code: str):
    result = deobfuscate(code)
    assert "deobfuscated" in result.code


def test_unwrap_one_blob():
    data = zlib.compress(b"deobfuscated")
    assert unwrap(repr(data)) == "deobfuscated"


def test_unwrap_longest_blob():
    blob = repr(zlib.compress(b"blob"))
    blobby = repr(zlib.compress(b"blobby"))

    assert unwrap(f"{blob}\n{blobby}") == "blobby"
