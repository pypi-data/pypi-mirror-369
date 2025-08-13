## Copyright 2009-2021 Intel Corporation
## SPDX-License-Identifier: Apache-2.0

# use default install config
INCLUDE("${CMAKE_CURRENT_LIST_DIR}/embree-config-install.cmake")

# and override path variables to match for build directory
SET(EMBREE_INCLUDE_DIRS /project/build/_deps/embree-src/include)
SET(EMBREE_LIBRARY /project/build/_deps/embree-build/libembree4.so.4)
SET(EMBREE_LIBRARIES ${EMBREE_LIBRARY})
