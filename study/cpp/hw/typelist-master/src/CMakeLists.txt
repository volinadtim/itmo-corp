add_library(typelist INTERFACE)

# Add sources
target_sources(typelist
    PUBLIC FILE_SET HEADERS FILES
        "typelist.h"
)
