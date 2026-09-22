add_library(repl-lib)

# Add sources
target_sources(repl-lib
    PUBLIC FILE_SET HEADERS FILES
        "example.h"
    PRIVATE
        "example.cpp"
)

add_subdirectory(rpc)
