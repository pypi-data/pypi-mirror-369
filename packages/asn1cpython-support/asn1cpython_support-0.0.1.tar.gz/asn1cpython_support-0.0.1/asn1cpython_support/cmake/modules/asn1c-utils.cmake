# ===============================================================
# Common utilities for ASN.1 to Python C extension integration
# Provided by the asn1c-bindings CMake package
# ===============================================================

# ---------------------------------------------------------------
# function: asn1c_generate
#
# Purpose:
#   Runs the ASN.1 compiler (`asn1c`) to generate the C source
#   files and Python type stubs for the specified extension
#   module.
#
#   This is typically called at **CMake configure time** so that
#   the generated sources are available before the build step.
#
# Input variables (must be set before calling):
#   - A1C_PATH             : Path to the ASN.1 compiler executable.
#   - A1C_EXT_NAME         : Full extension module name (may include dots).
#   - A1C_EXT_BASENAME     : Module base name (without any submodule prefix).
#   - A1C_SKELETONS_PATH   : Path to asn1c skeleton files.
#   - A1C_GENERATED_DIR    : Directory where generated C/Python files will be placed.
#   - A1C_BER, A1C_OER, A1C_UPER, A1C_PER,
#     A1C_XER, A1C_JER, A1C_PRINT : Flags controlling encoder/decoder generation.
#   - A1C_EXTRA_ARGS       : Any extra arguments for the ASN.1 compiler. (OPTIONAL)
#   - A1C_SOURCE_FILES     : List of ASN.1 specification files to compile.
# ---------------------------------------------------------------
function(asn1c_generate)
    message(STATUS "[asn1c-bindings] Generating ASN.1 sources for module '${A1C_EXT_NAME}'")

    execute_process(
        COMMAND ${A1C_PATH}
        -M "${A1C_EXT_BASENAME}"
        -S "${A1C_SKELETONS_PATH}"
        -D "${A1C_GENERATED_DIR}"
        -gen-python
        -no-gen-example
        -no-gen-autotools
        -fcompound-names
        ${A1C_BER} ${A1C_OER} ${A1C_UPER} ${A1C_PER}
        ${A1C_XER} ${A1C_JER} ${A1C_PRINT} ${A1C_EXTRA_ARGS}
        ${A1C_SOURCE_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        RESULT_VARIABLE A1C_GENERATION_RESULT
        OUTPUT_VARIABLE A1C_GENERATION_STDOUT
        ERROR_VARIABLE A1C_GENERATION_STDERR
    )

    if(NOT A1C_GENERATION_RESULT EQUAL 0)
        message(FATAL_ERROR "[asn1c-bindings] ASN.1 compiler failed:\n${A1C_GENERATION_STDERR}")
    endif()
endfunction()

# ---------------------------------------------------------------
# function: asn1c_install_stub
#
# Purpose:
#   Installs the generated Python type stub file (`.pyi`) into
#   the correct package directory during `make install`.
#
# Parameters:
#   DESTINATION_DIR : The install path inside the Python package
#                     (relative to the package root).
#
# Input variables (must be set before calling):
#   - A1C_GENERATED_DIR  : Directory containing generated files.
#   - A1C_EXT_BASENAME   : Base name for the module (used for renaming).
# ---------------------------------------------------------------
function(asn1c_install_stub DESTINATION_DIR)
    install(
        FILES ${A1C_GENERATED_DIR}/py_module.pyi
        DESTINATION ${DESTINATION_DIR}
        RENAME "${A1C_EXT_BASENAME}.pyi"
    )
endfunction()
