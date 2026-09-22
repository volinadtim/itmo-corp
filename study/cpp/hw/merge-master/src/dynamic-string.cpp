#include "dynamic-string.h"

#include <cstdlib>

bool string_init(DynamicString* string, std::size_t capacity) {
  char* new_data = static_cast<char*>(std::malloc(capacity));
  if (new_data == nullptr) {
    return false;
  }
  string->data = new_data;
  string->size = 0;
  string->capacity = capacity;
  return true;
}

void string_free(DynamicString* string) {
  std::free(string->data);
}

bool string_push_back(DynamicString* string, char ch) {
  if (string->size == string->capacity) {
    std::size_t new_capacity = string->capacity * 2;
    char* new_data = static_cast<char*>(std::realloc(string->data, new_capacity));
    if (new_data == nullptr) {
      return false;
    }
    string->data = new_data;
    string->capacity = new_capacity;
  }
  string->data[string->size] = ch;
  string->size++;
  return true;
}
