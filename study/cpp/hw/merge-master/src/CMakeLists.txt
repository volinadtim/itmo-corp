add_executable(merge)

target_sources(merge
    PRIVATE
        "main.cpp"
        "dynamic-string.cpp"
    PUBLIC FILE_SET HEADERS FILES
        "dynamic-string.h"
)

ct_set_compiler_warnings(merge)
