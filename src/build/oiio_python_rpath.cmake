#
# Copyright Contributors to the OpenRV Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Usage: cmake -DMODULE_DIR=<.../site-packages/OpenImageIO> -P oiio_python_rpath.cmake
#
# OIIO installs its Python module with absolute build-tree RPATHs. Replace them
# with paths that resolve to RV's lib directory from both staged locations:
# lib/python3.x/site-packages/OpenImageIO and plugins/Python/OpenImageIO.

IF(NOT MODULE_DIR)
  MESSAGE(FATAL_ERROR "MODULE_DIR is not set.")
ENDIF()

FILE(GLOB _modules "${MODULE_DIR}/OpenImageIO*.so")
IF(NOT _modules)
  MESSAGE(FATAL_ERROR "No OpenImageIO Python module in ${MODULE_DIR}")
ENDIF()

FOREACH(
  _module
  ${_modules}
)
  FILE(RPATH_SET FILE ${_module} NEW_RPATH "$ORIGIN/../../..:$ORIGIN/../../../lib")
ENDFOREACH()
