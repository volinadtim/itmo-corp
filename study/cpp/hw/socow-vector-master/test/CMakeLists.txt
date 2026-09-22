add_executable(tests)

# Add sources
target_sources(tests
    PRIVATE FILE_SET HEADERS FILES
        element.h
        test-utils.h
    PRIVATE
        element.cpp
        traits-test.cpp
        vector-test.cpp
)

# Setup warnings
ct_set_compiler_warnings(tests)

# Link with solution
target_link_libraries(tests PRIVATE socow-vector)

# Link with dependencies
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
