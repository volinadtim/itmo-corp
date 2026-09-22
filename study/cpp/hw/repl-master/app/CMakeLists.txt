add_executable(repl-app)

# Add sources
target_sources(repl-app
    PRIVATE
        "main.cpp"
)

# Setup warnings
ct_set_compiler_warnings(repl-app)

# Link with repl libs
target_link_libraries(repl-app PRIVATE repl-lib repl-rpc-lib)
