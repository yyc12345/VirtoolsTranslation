cmake_minimum_required(VERSION 3.12)
project(NlpCodec LANGUAGES CXX)

# find packages
find_package(ZLIB REQUIRED)

# set standard
set(CMAKE_CXX_STANDARD 17)

# generate program
add_executable(NlpCodec NlpCodec.cpp)
target_link_libraries(NlpCodec
PRIVATE
	${ZLIB_LIBRARIES}
)
target_include_directories(NlpCodec
PRIVATE
	${ZLIB_INCLUDE_DIRS}
)
