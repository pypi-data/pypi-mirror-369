# Simple and small script to query the location of CMake files used to build
# new ASN.1 extensions.
import argparse

from asn1cpython_support import VERSION, cmake_dir


def main():
    parser = argparse.ArgumentParser("asn1cpython-support")
    parser.add_argument(
        "--cmake-dir",
        action="store_true",
        help="Print CMake installation directory",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version",
    )
    args = parser.parse_args()

    if args.cmake_dir:
        print(cmake_dir())

    if args.version:
        print(VERSION)


if __name__ == "__main__":
    main()
