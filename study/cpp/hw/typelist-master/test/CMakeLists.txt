add_executable(tests)

# Add sources
target_sources(tests
    PRIVATE
        typelist-test.cpp
)

# Setup warnings
ct_set_compiler_warnings(tests)

# Link with solution
target_link_libraries(tests PRIVATE typelist)

# Link with dependencies
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
