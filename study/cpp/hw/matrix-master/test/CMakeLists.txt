add_executable(matrix-tests)

# Add sources
target_sources(matrix-tests
    PUBLIC FILE_SET HEADERS FILES
        test-helpers.h
    PRIVATE
        col-iterator-test.cpp
        constructors-test.cpp
        operations-test.cpp
        traits-test.cpp
        views-test.cpp
)

# Setup warnings
ct_set_compiler_warnings(matrix-tests)

# Link with matrix
target_link_libraries(matrix-tests PRIVATE matrix)

# Link with dependencies
target_link_libraries(matrix-tests PRIVATE GTest::gtest GTest::gtest_main)
