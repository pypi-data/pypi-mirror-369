# ===============================================================
# Common ASN.1 Compiler (asn1c) CMake Settings
# ===============================================================
#
# Table of configurable variables:
# +-----------------------+----------------------------------+------------------------------------+
# | Variable              | Default                          | Description                        |
# +=======================+==================================+====================================+
# | A1C_PATH              | asn1c                            | Path to ASN.1 compiler binary      |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_SKELETONS_PATH    | /usr/local/share/asn1c/          | Path to ASN.1 skeletons directory  |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_BER       | *unset*                          | Disable BER codec generation       |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_OER       | *unset*                          | Disable OER codec generation       |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_UPER      | *unset*                          | Disable UPER codec generation      |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_APER      | *unset*                          | Disable APER codec generation      |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_XER       | *unset*                          | Disable XER codec generation       |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_JER       | *unset*                          | Disable JER codec generation       |
# +-----------------------+----------------------------------+------------------------------------+
# | A1C_DISABLE_PRINT     | *unset*                          | Disable print function generation  |
# +-----------------------+----------------------------------+------------------------------------+


# ---------------------------------------------------------------
# function: set_from_env_or_default
#
# Purpose:
#   Assigns a variable’s value based on priority:
#     1. If an environment variable with the same name is set, use it.
#     2. Else if a CMake variable is already defined, keep it.
#     3. Otherwise, assign a provided default value.
#
# Arguments:
#   VAR     : The variable name (string, no `$`).
#   DEFAULT : The default value to assign if unset.
#
# Behavior:
#   - The resolved value is set in the **parent scope** so the
#     caller’s context receives it.
# ---------------------------------------------------------------
function(set_from_env_or_default VAR DEFAULT)
    if(DEFINED ENV{${VAR}})
        # Environment variable takes highest priority
        set(${VAR} $ENV{${VAR}} PARENT_SCOPE)
    elseif(DEFINED ${VAR})
        # Already defined in CMake; preserve value
        set(${VAR} ${${VAR}} PARENT_SCOPE)
    else()
        # Assign default
        set(${VAR} ${DEFAULT} PARENT_SCOPE)
    endif()
endfunction()

# ---------------------------------------------------------------
# function: set_codec_flag
#
# Purpose:
#   Sets a codec generation flag for asn1c based on whether
#   the codec is disabled.
#
# Arguments:
#   FLAG_NAME   : The codec identifier (e.g., BER, OER, UPER).
#   ENABLE_STR  : The compiler flag to enable this codec.
#   DISABLE_STR : The compiler flag to disable this codec.
#
# Behavior:
#   - If the disabling variable (either environment variable
#     `A1C_DISABLE_<FLAG_NAME>` or CMake variable with same name)
#     is set, the disable flag is stored in `A1C_<FLAG_NAME>`.
#   - Otherwise, the enable flag is stored in `A1C_<FLAG_NAME>`.
#   - The result is placed in the parent scope.
# ---------------------------------------------------------------
function(set_codec_flag FLAG_NAME ENABLE_STR DISABLE_STR)
    if(DEFINED ENV{A1C_DISABLE_${FLAG_NAME}} OR DEFINED A1C_DISABLE_${FLAG_NAME})
        # Disabling variable is present → use disable flag
        set(A1C_${FLAG_NAME} "${DISABLE_STR}" PARENT_SCOPE)
    else()
        # Otherwise enable codec
        set(A1C_${FLAG_NAME} "${ENABLE_STR}" PARENT_SCOPE)
    endif()
endfunction()


set_from_env_or_default(A1C_PATH "asn1c")
set_from_env_or_default(A1C_SKELETONS_PATH "/usr/local/share/asn1c/")
set_codec_flag(BER   "-gen-BER"   "-no-gen-BER")
set_codec_flag(OER   "-gen-OER"   "-no-gen-OER")
set_codec_flag(UPER  "-gen-UPER"  "-no-gen-UPER")
set_codec_flag(APER  "-gen-APER"  "-no-gen-APER")
set_codec_flag(XER   "-gen-XER"   "-no-gen-XER")
set_codec_flag(JER   "-gen-JER"   "-no-gen-JER")
set_codec_flag(PRINT "-gen-print" "-no-gen-print")
