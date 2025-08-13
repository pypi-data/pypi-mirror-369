# Install script for directory: /Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/var/folders/y6/nj790rtn62lfktb1sh__79hc0000gn/T/tmpddrielv8/wheel/platlib")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/include/embree4")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man" TYPE DIRECTORY FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/man/man3")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/LICENSE.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/CHANGELOG.md")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/README.md")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/readme.pdf")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/third-party-programs.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/third-party-programs-TBB.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/third-party-programs-OIDN.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/third-party-programs-DPCPP.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/embree4" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-src/third-party-programs-oneAPI-DPCPP.txt")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/embree-vars.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "lib" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/." TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/embree-vars.csh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/embree-4.3.3" TYPE FILE RENAME "embree-config.cmake" FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/embree-config-install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "devel" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/embree-4.3.3" TYPE FILE FILES "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/embree-config-version.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/common/cmake_install.cmake")
  include("/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/kernels/cmake_install.cmake")
  include("/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/tests/cmake_install.cmake")

endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/Users/runner/work/ViennaPS/ViennaPS/build/_deps/embree-build/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
