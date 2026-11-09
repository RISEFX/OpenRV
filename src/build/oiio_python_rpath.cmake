#
# Copyright Contributors to the OpenRV Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Usage: cmake -DMODULE_DIR=<directory of the installed OpenImageIO package> -P oiio_python_rpath.cmake
#
# OIIO installs its Python module with absolute build-tree RPATHs. Replace them
# with a path that resolves to RV's lib directory from plugins/Python/OpenImageIO.

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
  FILE(RPATH_SET FILE ${_module} NEW_RPATH "$ORIGIN/../../../lib")
ENDFOREACH()
