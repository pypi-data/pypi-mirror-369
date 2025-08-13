# asn1c-extension.cmake
# =====================================================================
# This file defines the public CMake API function `asn1c_add_extension`,
# which automates building a Python C-extension module from ASN.1
# source files using the `asn1c` compiler.
#
# It supports both top-level modules (e.g. "_example_mod") and
# submodule layouts (e.g. "subpackage._example_mod"), with automatic
# detection of ASN.1 source files and generated code handling.
#
# It relies on helper functions defined in other CMake includes:
#   - set_from_env_or_default()
#   - asn1c_generate()
#   - asn1c_install_stub()
# =====================================================================
include_guard(GLOBAL)

if (CMAKE_VERSION VERSION_LESS 3.18)
  set(DEV_MODULE Development)
else()
  set(DEV_MODULE Development.Module)
endif()

find_package(Python REQUIRED COMPONENTS Interpreter ${DEV_MODULE})

# ---------------------------------------------------------------------
# If the build type is not set (single-config generators like Makefiles),
# default to Release and provide the standard build type options.
# ---------------------------------------------------------------------
if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# =====================================================================
# asn1c_add_extension()
#
# Adds a Python extension module built from ASN.1 files using `asn1c`.
#
# Arguments:
#   NAME <name>        - Required. Module name (e.g. "_example_mod").
#                        If SUBMODULE is given, NAME may include dots
#                        for package hierarchy, e.g. "pkg._example_mod".
#   SUBMODULE          - Optional flag. Treat NAME as a dotted module
#                        path and adjust output/install paths accordingly.
#   ASN_FILES <files>  - Optional. Explicit list of ASN.1 files. If not
#                        given, the function will search the current
#                        source directory (*.asn) or fall back to
#                        environment/project variable A1C_ASN_FILES.
# =====================================================================
function(asn1c_add_extension)
    cmake_parse_arguments(
        A1C_EXT              # Prefix for parsed arguments
        "SUBMODULE"          # Boolean options
        "NAME"               # Single-value arguments
        "ASN_FILES"          # Multi-value arguments
        ${ARGN}              # All passed arguments
    )

    message(STATUS "[asn1c-bindings] ==================  Adding ASN.1 extension   ==================")
    if(NOT A1C_EXT_NAME)
        message(FATAL_ERROR "[asn1c-bindings] asn1c_add_extension() requires NAME argument")
    endif()

    # If SUBMODULE is set, treat NAME as dotted path and convert to filesystem path
    if(A1C_EXT_SUBMODULE)
        string(REPLACE "." "/" A1C_EXT_PATH ${A1C_EXT_NAME})
        get_filename_component(A1C_EXT_BASENAME ${A1C_EXT_PATH} NAME)
    else()
        set(A1C_EXT_PATH ${A1C_EXT_NAME})
        set(A1C_EXT_BASENAME ${A1C_EXT_NAME})
    endif()

    # --------------------------------------------------------------
    # ASN.1 source file resolution priority:
    #   1. ASN_FILES argument
    #   2. *.asn files in current source directory
    #   3. Environment variable A1C_ASN_FILES
    #   4. CMake variable A1C_ASN_FILES
    # If none found — fatal error.
    # --------------------------------------------------------------
    if(A1C_EXT_ASN_FILES)
        set(A1C_SOURCE_FILES ${A1C_EXT_ASN_FILES})
    else()
        file(GLOB LOCAL_ASN_FILES RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/*.asn")
        if(LOCAL_ASN_FILES)
            set(A1C_SOURCE_FILES "")
            foreach(_f ${LOCAL_ASN_FILES})
                list(APPEND A1C_SOURCE_FILES "${CMAKE_CURRENT_SOURCE_DIR}/${_f}")
            endforeach()
        elseif(DEFINED ENV{A1C_ASN_FILES})
            # Allow env var to specify files, separated by semicolons, commas, or spaces
            string(REPLACE ";" " " _tmp "$ENV{A1C_ASN_FILES}")
            string(REPLACE "," " " _tmp "${_tmp}")
            separate_arguments(_tmp)
            set(A1C_SOURCE_FILES ${_tmp})
        elseif(DEFINED A1C_ASN_FILES)
            set(A1C_SOURCE_FILES ${A1C_ASN_FILES})
        else()
            message(FATAL_ERROR "[asn1c-bindings] No ASN.1 files found for ${A1C_EXT_NAME}; place .asn files in project root or pass ASN_FILES to asn1c_add_extension().")
        endif()
    endif()

    # --------------------------------------------------------------
    # Prepare output directory for generated code
    # --------------------------------------------------------------
    set_from_env_or_default(A1C_GENERATED_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/generated/${A1C_EXT_NAME}")
    file(MAKE_DIRECTORY ${A1C_GENERATED_DIR})

    message(STATUS "[asn1c-bindings] Configuring extension: ${A1C_EXT_NAME}")
    message(STATUS "[asn1c-bindings]  - module basename: ${A1C_EXT_BASENAME}")
    message(STATUS "[asn1c-bindings]  - generated dir: ${A1C_GENERATED_DIR}")
    foreach(_f ${A1C_SOURCE_FILES})
        message(STATUS "[asn1c-bindings]  - ASN.1 source: ${_f}")
    endforeach()

    # --------------------------------------------------------------
    # Generate ASN.1 C sources
    # --------------------------------------------------------------
    asn1c_generate()
    file(GLOB A1C_GENERATED_SOURCES "${A1C_GENERATED_DIR}/*.c")
    if(NOT A1C_GENERATED_SOURCES)
        message(FATAL_ERROR "No generated C sources found in ${A1C_GENERATED_DIR}!")
    endif()

    # --------------------------------------------------------------
    # Build the Python extension module
    # WITH_SOABI ensures the extension has the correct ABI tag
    # --------------------------------------------------------------
    python_add_library(${A1C_EXT_BASENAME} MODULE ${A1C_GENERATED_SOURCES} WITH_SOABI)
    target_include_directories(${A1C_EXT_BASENAME} PRIVATE ${A1C_GENERATED_DIR})

    if(A1C_EXT_SUBMODULE)
        get_filename_component(SUBMODULE_DIR ${A1C_EXT_PATH} DIRECTORY)
        install(TARGETS ${A1C_EXT_BASENAME} DESTINATION ${SKBUILD_PROJECT_NAME}/${SUBMODULE_DIR})
        asn1c_install_stub(${SKBUILD_PROJECT_NAME}/${SUBMODULE_DIR})
    else()
        install(TARGETS ${A1C_EXT_BASENAME} DESTINATION ${SKBUILD_PROJECT_NAME})
        asn1c_install_stub(${SKBUILD_PROJECT_NAME})
    endif()

    message(STATUS "[asn1c-bindings] Configured ASN.1 extension: ${A1C_EXT_NAME}")
endfunction()
