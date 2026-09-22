#pragma once

#include <cstddef>

struct DynamicString {
  char* data;
  std::size_t size;
  std::size_t capacity;
};

[[nodiscard]] bool string_init(DynamicString* string, std::size_t capacity);
void string_free(DynamicString* string);

[[nodiscard]] bool string_push_back(DynamicString* string, char ch);
