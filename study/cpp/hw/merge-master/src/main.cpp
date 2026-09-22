#include "dynamic-string.h"

#include <cstdio>
#include <cstdlib>

int main() {
  DynamicString string;
  string_init(&string, 1);

  for (char c : "Hello, World!") {
    string_push_back(&string, c);
  }

  // Oral exercise:
  // 1. Before running it, can you guess what will be printed?
  // 2. Is such call OK for our `DynamicString` in general?
  // 3. If not, what would be the better way?
  std::printf(
      "size=%d, capacity=%d, text=\"%s\"\n",
      static_cast<int>(string.size),
      static_cast<int>(string.capacity),
      string.data
  );

  string_free(&string);

  return EXIT_SUCCESS;
}
