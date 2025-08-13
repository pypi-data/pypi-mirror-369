import pathlib

VERSION = "0.0.1"


def cmake_dir() -> str:
    """Returns the path to the CMake files used to build new ASN.1 extensions."""
    return str(pathlib.Path(__file__).parent / "cmake")
