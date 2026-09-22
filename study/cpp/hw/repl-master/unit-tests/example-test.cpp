#include "example.h"

#include <gtest/gtest.h>

namespace ct_test {

TEST(ExampleTest, TwoPlusTwoIsFour) {
  ASSERT_EQ(ct::sum(2, 2), 4);
}

} // namespace ct_test
