#include "matrix.h"
#include "test-helpers.h"

#include <gtest/gtest.h>

#include <algorithm>
#include <cstddef>
#include <iterator>
#include <memory>
#include <utility>

namespace ct::test {

class ColIteratorTest : public ::testing::Test {
protected:
  using EMatrix = Matrix<Element>;

  EMatrix m = EMatrix({
      {1, 2, 3},
      {4, 5, 6},
      {11, 12, 13},
      {14, 15, 16},
  });
};

namespace {

template <typename It>
It linear_advance(It it, std::iter_difference_t<It> n) {
  while (n > 0) {
    --n;
    ++it;
  }
  while (n < 0) {
    ++n;
    --it;
  }
  return it;
}

std::ptrdiff_t as_diff(std::size_t n) {
  return static_cast<std::ptrdiff_t>(n);
}

} // namespace

TEST_F(ColIteratorTest, NonConstToConstConversion) {
  EMatrix::ColIterator begin = m.col_begin(1);
  EMatrix::ConstColIterator cbegin = begin;
  EXPECT_EQ(cbegin, std::as_const(m).col_begin(1));
  EXPECT_EQ(cbegin, begin);

  EMatrix::ColIterator end = m.col_end(1);
  EMatrix::ConstColIterator cend = end;
  EXPECT_EQ(cend, std::as_const(m).col_end(1));
  EXPECT_EQ(cend, end);
}

TEST_F(ColIteratorTest, CopyConstructor) {
  EMatrix::ColIterator it1 = m.col_begin(1);
  EMatrix::ColIterator it2 = it1;
  EXPECT_EQ(it2, it1);

  ++it2;
  EXPECT_NE(it2, it1);
}

TEST_F(ColIteratorTest, DefaultConstructor) {
  EMatrix::ColIterator it;
  it = m.col_begin(1);

  EMatrix::ConstColIterator cit;
  cit = m.col_begin(1);

  EXPECT_EQ(cit, it);
}

TEST_F(ColIteratorTest, Indirection) {
  auto it = m.col_begin(1);
  auto end = std::as_const(m).col_end(1);

  for (std::size_t row_idx = 0; row_idx < m.rows(); ++row_idx) {
    ASSERT_NE(it, end);
    EXPECT_EQ(*it, (m[row_idx, 1]));
    *it = 42;
    ++it;
  }
  EXPECT_EQ(it, end);

  std::for_each(m.col_begin(1), m.col_end(1), [](Element x) {
    EXPECT_EQ(x, 42);
  });
}

TEST_F(ColIteratorTest, MemberAccess) {
  auto it = m.col_begin(1);
  auto end = std::as_const(m).col_end(1);

  for (std::size_t row_idx = 0; row_idx < m.rows(); ++row_idx) {
    ASSERT_NE(it, end);
    EXPECT_EQ(it->value, (m[row_idx, 1]).value);
    it->value = 42;
    ++it;
  }
  EXPECT_EQ(it, end);

  std::for_each(m.col_begin(1), m.col_end(1), [](Element x) {
    EXPECT_EQ(x, 42);
  });
}

TEST_F(ColIteratorTest, Increment) {
  auto it = std::as_const(m).col_begin(1);

  EXPECT_EQ(std::to_address(++it), &(m[1, 1]));
  EXPECT_EQ(std::to_address(it), &(m[1, 1]));

  EXPECT_EQ(std::to_address(it++), &(m[1, 1]));
  EXPECT_EQ(std::to_address(it), &(m[2, 1]));
}

TEST_F(ColIteratorTest, Decrement) {
  auto it = std::as_const(m).col_end(1);

  EXPECT_EQ(std::to_address(--it), &(m[3, 1]));
  EXPECT_EQ(std::to_address(it), &(m[3, 1]));

  EXPECT_EQ(std::to_address(it--), &(m[3, 1]));
  EXPECT_EQ(std::to_address(it), &(m[2, 1]));
}

TEST_F(ColIteratorTest, AddDifference) {
  auto it = std::as_const(m).col_begin(1);

  EXPECT_EQ(it + m.rows(), m.col_end(1));

  for (std::ptrdiff_t i = 0; i <= as_diff(m.rows()); ++i) {
    EXPECT_EQ(it + i, linear_advance(it, i));
    EXPECT_EQ(i + it, linear_advance(it, i));

    auto it2 = it;
    it2 += i;
    EXPECT_EQ(it2, linear_advance(it, i));
  }
}

TEST_F(ColIteratorTest, SubtractDifference) {
  auto it = std::as_const(m).col_end(1);

  EXPECT_EQ(it - m.rows(), m.col_begin(1));

  for (std::ptrdiff_t i = 0; i <= as_diff(m.rows()); ++i) {
    EXPECT_EQ(it - i, linear_advance(it, -i));

    auto it2 = it;
    it2 -= i;
    EXPECT_EQ(it2, linear_advance(it, -i));
  }
}

TEST_F(ColIteratorTest, AddNegativeDifference) {
  auto it = std::as_const(m).col_end(1);

  EXPECT_EQ(it + -as_diff(m.rows()), m.col_begin(1));

  for (std::ptrdiff_t i = 0; i <= as_diff(m.rows()); ++i) {
    EXPECT_EQ(it + -i, linear_advance(it, -i));
    EXPECT_EQ(-i + it, linear_advance(it, -i));

    auto it2 = it;
    it2 += -i;
    EXPECT_EQ(it2, linear_advance(it, -i));
  }
}

TEST_F(ColIteratorTest, SubtractNegativeDifference) {
  auto it = std::as_const(m).col_begin(1);

  EXPECT_EQ(it - -as_diff(m.rows()), m.col_end(1));

  for (std::ptrdiff_t i = 0; i <= as_diff(m.rows()); ++i) {
    EXPECT_EQ(it - -i, linear_advance(it, i));

    auto it2 = it;
    it2 -= -i;
    EXPECT_EQ(it2, linear_advance(it, i));
  }
}

TEST_F(ColIteratorTest, IteratorDifference) {
  auto it = std::as_const(m).col_begin(1);
  auto end = m.col_end(1);

  EXPECT_EQ(it - it, 0);
  EXPECT_EQ(end - end, 0);
  EXPECT_EQ(end - it, m.rows());
  EXPECT_EQ(it - end, -as_diff(m.rows()));

  ++it;
  --end;

  EXPECT_EQ(end - it, m.rows() - 2);
  EXPECT_EQ(it - end, -as_diff(m.rows() - 2));
}

TEST_F(ColIteratorTest, Subscript) {
  auto it = std::as_const(m).col_begin(1);

  EXPECT_EQ(it[0], (m[0, 1]));
  EXPECT_EQ(it[1], (m[1, 1]));

  EXPECT_EQ(&it[0], &(m[0, 1]));
  EXPECT_EQ(&it[1], &(m[1, 1]));

  ++it;

  EXPECT_EQ(it[-1], (m[0, 1]));
  EXPECT_EQ(it[0], (m[1, 1]));
  EXPECT_EQ(it[1], (m[2, 1]));

  EXPECT_EQ(&it[-1], &(m[0, 1]));
  EXPECT_EQ(&it[0], &(m[1, 1]));
  EXPECT_EQ(&it[1], &(m[2, 1]));
}

TEST_F(ColIteratorTest, Compare) {
  auto it1 = std::as_const(m).col_begin(1);
  auto it2 = it1;

  EXPECT_EQ(it1, it2);
  EXPECT_LE(it1, it2);
  EXPECT_GE(it1, it2);

  EXPECT_FALSE(it1 < it2);
  EXPECT_FALSE(it1 > it2);

  ++it2;
  EXPECT_NE(it1, it2);
  EXPECT_LE(it1, it2);
  EXPECT_LT(it1, it2);
  EXPECT_GE(it2, it1);
  EXPECT_GT(it2, it1);

  auto end = m.col_end(1);

  EXPECT_EQ(end, end);
  EXPECT_LE(end, end);
  EXPECT_GE(end, end);

  EXPECT_FALSE(end < end);
  EXPECT_FALSE(end > end);

  EXPECT_NE(it2, end);
  EXPECT_LT(it2, end);
  EXPECT_GT(end, it2);
}

} // namespace ct::test
