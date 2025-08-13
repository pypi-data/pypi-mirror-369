# ASN.1c Python Bndings Support Files

`asn1cpython-support` is a small Python helper package that provides build-time
support utilities for Python packages using the modified
[asn1c](https://github.com/MatrixEditor/asn1c-bindings) compiler to generate C
sources from ASN.1 specifications. Documentation is here:
[matrixeditor.github.io/asn1c-bindings](https://matrixeditor.github.io/asn1c-bindings/).

Its primary purpose is to bridge Python packaging tools (such as
[scikit-build-core](https://scikit-build-core.readthedocs.io/en/latest/)) with
the asn1c-bindings CMake package, ensuring that ASN.1 source files can be
compiled into Python extension modules seamlessly.

## Usage in CMake

When building a Python extension module that uses ASN.1 specifications, you can
retrieve the CMake package path like this:

```cmake
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m asn1cpython_support --cmake-dir
    OUTPUT_STRIP_TRAILING_WHITESPACE
    OUTPUT_VARIABLE asn1c-bindings_ROOT
)
find_package(asn1c-bindings CONFIG REQUIRED)
```

## Installation

```bash
pip install asn1cpython-support
```

### Example

A typical `pyproject.toml` snippet using this package with *scikit-build-core*:

```toml
[build-system]
# This requirement will make all required files available at build time
requires = ["scikit-build-core~=0.9.0", "asn1cpython-support"]
build-backend = "scikit_build_core.build"

[tool.scikit-build]
cmake.minimum-version = "3.15"
# ...
```

## License

MIT License — see LICENSE for details.