cmake_minimum_required(VERSION 3.12)
project(NlpEncoder LANGUAGES CXX)

# find packages
find_package(ZLIB REQUIRED)

# set standard
set(CMAKE_CXX_STANDARD 17)

# generate program
add_executable(NlpEncoder NlpEncoder.cpp)
target_link_libraries(NlpEncoder
PRIVATE
	${ZLIB_LIBRARIES}
)
target_include_directories(NlpEncoder
PRIVATE
	${ZLIB_INCLUDE_DIRS}
)
