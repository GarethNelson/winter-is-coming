cmake_minimum_required(VERSION 3.2)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")
set(CMAKE_CXX_STANDARD 11)

find_package(Crypto++ REQUIRED)

file(GLOB NODE_SRC "src/*.cpp")

include_directories(${CRYPTO++_INCLUDE_DIR})

add_executable(node ${NODE_SRC})

target_link_libraries(node ${CRYPTO++_LIBRARY})
