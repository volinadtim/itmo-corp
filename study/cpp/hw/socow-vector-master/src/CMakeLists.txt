add_library(socow-vector INTERFACE)

# Add sources
target_sources(socow-vector
    PUBLIC FILE_SET HEADERS FILES
        "socow-vector.h"
)
