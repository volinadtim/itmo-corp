#pragma once

#include "matrix.h"

#include <gtest/gtest.h>

#include <cstddef>

namespace ct::test {

struct Element {
  void* operator new[](std::size_t count) {
    allocations += count / sizeof(Element);
    return ::operator new[](count);
  }

  void operator delete[](void* ptr) {
    ::operator delete[](ptr);
  }

  Element() = default;

  Element(std::size_t value)
      : value(value) {}

  friend Element operator+(const Element& lhs, const Element& rhs) {
    return {lhs.value + rhs.value};
  }

  friend Element operator-(const Element& lhs, const Element& rhs) {
    return {lhs.value - rhs.value};
  }

  friend Element operator*(const Element& lhs, const Element& rhs) {
    return {lhs.value * rhs.value};
  }

  Element& operator+=(const Element& other) {
    value += other.value;
    return *this;
  }

  Element& operator-=(const Element& other) {
    value -= other.value;
    return *this;
  }

  Element& operator*=(const Element& other) {
    value *= other.value;
    return *this;
  }

  friend bool operator==(const Element&, const Element&) = default;

  friend std::ostream& operator<<(std::ostream& out, const Element& e) {
    return out << e.value;
  }

public:
  inline static std::size_t allocations;

  static void reset_allocations() {
    allocations = 0;
  }

public:
  std::size_t value;
};

inline void expect_allocations(std::size_t expected_allocations) {
  EXPECT_LE(Element::allocations, expected_allocations);
}

inline std::size_t elem(std::size_t row_idx, std::size_t col_idx) {
  return row_idx * 101 + col_idx * 7;
}

template <typename T>
void fill(Matrix<T>& a) {
  for (std::size_t row_idx = 0; row_idx < a.rows(); ++row_idx) {
    for (std::size_t col_idx = 0; col_idx < a.cols(); ++col_idx) {
      a[row_idx, col_idx] = elem(row_idx, col_idx);
    }
  }
}

template <typename T>
void expect_empty(const Matrix<T>& m) {
  EXPECT_EQ(m.rows(), 0);
  EXPECT_EQ(m.cols(), 0);
  EXPECT_EQ(m.size(), 0);
  EXPECT_TRUE(m.empty());
  EXPECT_EQ(m.data(), nullptr);
}

#define EXPECT_MATRIX_ELEM_EQ(matrix, row_idx, col_idx, expected)                                                      \
  EXPECT_EQ((matrix[row_idx, col_idx]), expected) << " where row_idx=" << row_idx << ", col_idx=" << col_idx

template <typename T>
void expect_equal(const Matrix<T>& actual, const Matrix<T>& expected) {
  EXPECT_EQ(actual.rows(), expected.rows());
  EXPECT_EQ(actual.cols(), expected.cols());
  EXPECT_EQ(actual.size(), expected.size());
  EXPECT_EQ(actual.empty(), expected.empty());
  EXPECT_EQ(actual.data() == nullptr, expected.data() == nullptr);

  for (std::size_t row_idx = 0; row_idx < expected.rows(); ++row_idx) {
    for (std::size_t col_idx = 0; col_idx < expected.cols(); ++col_idx) {
      T expected_value = expected[row_idx, col_idx];
      EXPECT_MATRIX_ELEM_EQ(actual, row_idx, col_idx, expected_value);
    }
  }
}

} // namespace ct::test
