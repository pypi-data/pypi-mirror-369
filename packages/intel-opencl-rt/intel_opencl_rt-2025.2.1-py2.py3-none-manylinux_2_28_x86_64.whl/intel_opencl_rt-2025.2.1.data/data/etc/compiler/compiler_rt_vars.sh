#!/bin/sh
# shellcheck shell=sh

# Copyright Intel Corporation
# SPDX-License-Identifier: MIT
# https://opensource.org/licenses/MIT


# ############################################################################

# Copy and include at the top of your `env/vars.sh` script (don't forget to
# remove the test/example code at the end of this file). See the test/example
# code at the end of this file for more help.


# ############################################################################

# Get absolute path to this script.
# Uses `readlink` to remove links and `pwd -P` to turn into an absolute path.

# Usage:
#   script_dir=$(get_script_path "$script_rel_path")
#
# Inputs:
#   script/relative/pathname/scriptname
#
# Outputs:
#   /script/absolute/pathname

# executing function in a *subshell* to localize vars and effects on `cd`
get_script_path() (
  script="$1"
  while [ -L "$script" ] ; do
    # combining next two lines fails in zsh shell
    script_dir=$(command dirname -- "$script")
    script_dir=$(cd "$script_dir" && command pwd -P)
    script="$(readlink "$script")"
    case $script in
      (/*) ;;
       (*) script="$script_dir/$script" ;;
    esac
  done
  # combining next two lines fails in zsh shell
  script_dir=$(command dirname -- "$script")
  script_dir=$(cd "$script_dir" && command pwd -P)
  printf "%s" "$script_dir"
)


# ############################################################################

# Determine if we are being executed or sourced. Need to detect being sourced
# within an executed script, which can happen on a CI system. We also must
# detect being sourced at a shell prompt (CLI). The setvars.sh script will
# always source this script, but this script can also be called directly.

# We are assuming we know the name of this script, which is a reasonable
# assumption. This script _must_ be named "vars.sh" or it will not work
# with the top-level setvars.sh script. Making this assumption simplifies
# the process of detecting if the script has been sourced or executed. It
# also simplifies the process of detecting the location of this script.

# Using `readlink` to remove possible symlinks in the name of the script.
# Also, "ps -o comm=" is limited to a 15 character result, but it works
# fine here, because we are only looking for the name of this script or the
# name of the execution shell, both always fit into fifteen characters.

# TODO: Edge cases exist when executed by way of "/bin/sh setvars.sh"
# Most shells detect or fall thru to error message, sometimes ksh does not.
# This is an odd and unusual situation; not a high priority issue.

_vars_get_proc_name() {
  if [ -n "${ZSH_VERSION:-}" ] ; then
    script="$(ps -p "$$" -o comm=)"
  else
    script="$1"
    while [ -L "$script" ] ; do
      script="$(readlink "$script")"
    done
  fi
  basename -- "$script"
}

_vars_this_script_name="vars.sh"
if [ "$_vars_this_script_name" = "$(_vars_get_proc_name "$0")" ] ; then
  echo "   ERROR: Incorrect usage: this script must be sourced."
  echo "   Usage: . path/to/${_vars_this_script_name}"
  return 255 2>/dev/null || exit 255
fi


# ############################################################################

# Prepend path segment(s) to path-like env vars (PATH, etc.).

# prepend_path() avoids dangling ":" that affects some env vars (PATH)
# prepend_manpath() includes dangling ":" needed by MANPATH.
# PATH > https://www.gnu.org/software/libc/manual/html_node/Standard-Environment.html
# MANPATH > https://manpages.debian.org/stretch/man-db/manpath.1.en.html

# Usage:
#   env_var=$(prepend_path "$prepend_to_var" "$existing_env_var")
#   export env_var
#
#   env_var=$(prepend_manpath "$prepend_to_var" "$existing_env_var")
#   export env_var
#
# Inputs:
#   $1 == path segment to be prepended to $2
#   $2 == value of existing path-like environment variable

prepend_path() (
  path_to_add="$1"
  path_is_now="$2"

  if [ "" = "${path_is_now}" ] ; then   # avoid dangling ":"
    printf "%s" "${path_to_add}"
  else
    printf "%s" "${path_to_add}:${path_is_now}"
  fi
)

prepend_manpath() (
  path_to_add="$1"
  path_is_now="$2"

  if [ "" = "${path_is_now}" ] ; then   # include dangling ":"
    printf "%s" "${path_to_add}:"
  else
    printf "%s" "${path_to_add}:${path_is_now}"
  fi
)


# ############################################################################

# Extract the name and location of this sourced script.

# Generally, "ps -o comm=" is limited to a 15 character result, but it works
# fine for this usage, because we are primarily interested in finding the name
# of the execution shell, not the name of any calling script.

vars_script_name=""
vars_script_shell="$(ps -p "$$" -o comm=)"
# ${var:-} needed to pass "set -eu" checks
# see https://unix.stackexchange.com/a/381465/103967
# see https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_06_02
if [ -n "${ZSH_VERSION:-}" ] && [ -n "${ZSH_EVAL_CONTEXT:-}" ] ; then     # zsh 5.x and later
  # shellcheck disable=2249
  case $ZSH_EVAL_CONTEXT in (*:file*) vars_script_name="${(%):-%x}" ;; esac ;
elif [ -n "${KSH_VERSION:-}" ] ; then                                     # ksh, mksh or lksh
  if [ "$(set | grep -Fq "KSH_VERSION=.sh.version" ; echo $?)" -eq 0 ] ; then # ksh
    vars_script_name="${.sh.file}" ;
  else # mksh or lksh or [lm]ksh masquerading as ksh or sh
    # force [lm]ksh to issue error msg; which contains this script's path/filename, e.g.:
    # mksh: /home/ubuntu/intel/oneapi/vars.sh[137]: ${.sh.file}: bad substitution
    vars_script_name="$( (echo "${.sh.file}") 2>&1 )" || : ;
    vars_script_name="$(expr "${vars_script_name:-}" : '^.*sh: \(.*\)\[[0-9]*\]:')" ;
  fi
elif [ -n "${BASH_VERSION:-}" ] ; then        # bash
  # shellcheck disable=2128
  (return 0 2>/dev/null) && vars_script_name="${BASH_SOURCE}" ;
elif [ "dash" = "$vars_script_shell" ] ; then # dash
  # force dash to issue error msg; which contains this script's rel/path/filename, e.g.:
  # dash: 146: /home/ubuntu/intel/oneapi/vars.sh: Bad substitution
  vars_script_name="$( (echo "${.sh.file}") 2>&1 )" || : ;
  vars_script_name="$(expr "${vars_script_name:-}" : '^.*dash: [0-9]*: \(.*\):')" ;
elif [ "sh" = "$vars_script_shell" ] ; then   # could be dash masquerading as /bin/sh
  # force a shell error msg; which should contain this script's path/filename
  # sample error msg shown; assume this file is named "vars.sh"; as required by setvars.sh
  vars_script_name="$( (echo "${.sh.file}") 2>&1 )" || : ;
  if [ "$(printf "%s" "$vars_script_name" | grep -Eq "sh: [0-9]+: .*vars\.sh: " ; echo $?)" -eq 0 ] ; then # dash as sh
    # sh: 155: /home/ubuntu/intel/oneapi/vars.sh: Bad substitution
    vars_script_name="$(expr "${vars_script_name:-}" : '^.*sh: [0-9]*: \(.*\):')" ;
  fi
else  # unrecognized shell or dash being sourced from within a user's script
  # force a shell error msg; which should contain this script's path/filename
  # sample error msg shown; assume this file is named "vars.sh"; as required by setvars.sh
  vars_script_name="$( (echo "${.sh.file}") 2>&1 )" || : ;
  if [ "$(printf "%s" "$vars_script_name" | grep -Eq "^.+: [0-9]+: .*vars\.sh: " ; echo $?)" -eq 0 ] ; then # dash
    # .*: 164: intel/oneapi/vars.sh: Bad substitution
    vars_script_name="$(expr "${vars_script_name:-}" : '^.*: [0-9]*: \(.*\):')" ;
  else
    vars_script_name="" ;
  fi
fi

if [ "" = "$vars_script_name" ] ; then
  >&2 echo "   ERROR: Unable to proceed: possible causes listed below."
  >&2 echo "   This script must be sourced. Did you execute or source this script?" ;
  >&2 echo "   Unrecognized/unsupported shell (supported: bash, zsh, ksh, m/lksh, dash)." ;
  >&2 echo "   May fail in dash if you rename this script (assumes \"vars.sh\")." ;
  >&2 echo "   Can be caused by sourcing from ZSH version 4.x or older." ;
  return 255 2>/dev/null || exit 255
fi


# ############################################################################

# For testing and simple demonstration.
# This is where you should put your component-specific env var settings.

my_script_path=$(get_script_path "${vars_script_name:-}")
component_root=$(dirname -- "${my_script_path}")

# Export required env vars for compiler package.
CMPLR_ROOT="${component_root}"; export CMPLR_ROOT

INTEL_TARGET_ARCH="intel64"
INTEL_TARGET_PLATFORM="linux"

while [ $# -gt 0 ]
do
  case "$1" in
  ia32)
    INTEL_TARGET_ARCH="ia32"
    shift
    ;;
  intel64)
    INTEL_TARGET_ARCH="intel64"
    shift
    ;;
  *)
    shift
    ;;
  esac
done

# This environment variable to switch il0 compiler to support ia32 mode.
if [ ${INTEL_TARGET_ARCH} = "ia32" ]; then
  export INTEL_TARGET_ARCH_IA32=ia32
else
  unset INTEL_TARGET_ARCH_IA32
fi

# intel64 libraries also be needed in ia32 target
LD_LIBRARY_PATH=$(prepend_path "${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/compiler/lib/intel64_lin" "${LD_LIBRARY_PATH:-}") ; export LD_LIBRARY_PATH
if [ ${INTEL_TARGET_ARCH} = "ia32" ]; then
  LD_LIBRARY_PATH=$(prepend_path "${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/compiler/lib/ia32_lin" "${LD_LIBRARY_PATH:-}") ; export LD_LIBRARY_PATH
fi

# OpenMP offload and CPU LLVM libraries and headers (includes OpenCL CPU run-time)
LD_LIBRARY_PATH=$(prepend_path "${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/lib:${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/lib/x64" "${LD_LIBRARY_PATH:-}") ; export LD_LIBRARY_PATH

if [ -z "${OCL_ICD_FILENAMES:-}" ]; then
  OCL_ICD_FILENAMES="${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/lib/x64/libintelocl.so"
else
  OCL_ICD_FILENAMES="${OCL_ICD_FILENAMES}:${CMPLR_ROOT}/${INTEL_TARGET_PLATFORM}/lib/x64/libintelocl.so"
fi
export OCL_ICD_FILENAMES

MANPATH=$(prepend_manpath "${CMPLR_ROOT}/documentation/en/man/common" "${MANPATH:-}") ; export MANPATH

DIAGUTIL_PATH=$(prepend_path "${CMPLR_ROOT}/etc/compiler/sys_check/sys_check.sh" "${DIAGUTIL_PATH:-}") ; export DIAGUTIL_PATH
