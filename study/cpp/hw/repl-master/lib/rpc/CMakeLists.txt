add_library(repl-rpc-lib)

# Add sources
target_sources(repl-rpc-lib
    PUBLIC FILE_SET HEADERS FILES
        "client.h"
    PRIVATE
        "client.cpp"
)

# Link with third-party dependencies
target_link_libraries(repl-rpc-lib PRIVATE httplib)
