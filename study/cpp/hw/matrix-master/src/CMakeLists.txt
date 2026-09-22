add_library(matrix INTERFACE)

# Add sources
target_sources(matrix
    PUBLIC FILE_SET HEADERS FILES
        "matrix.h"
)
