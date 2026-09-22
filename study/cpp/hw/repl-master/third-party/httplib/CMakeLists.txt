include(FetchContent)

message(STATUS "Fetching cpp_httplib...")
FetchContent_Declare(
    httplib
    URL https://github.com/yhirose/cpp-httplib/archive/refs/tags/v0.20.1.tar.gz
    SYSTEM
)
FetchContent_MakeAvailable(httplib)
