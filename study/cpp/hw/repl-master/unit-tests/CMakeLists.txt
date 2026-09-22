add_executable(repl-unit-tests)

# Add sources
target_sources(repl-unit-tests
    PRIVATE
        example-test.cpp
)

# Setup warnings
ct_set_compiler_warnings(repl-unit-tests)

# Link with 'repl-lib'
target_link_libraries(repl-unit-tests PRIVATE repl-lib)

# Link with third-party dependencies
target_link_libraries(repl-unit-tests PRIVATE GTest::gtest_main)
