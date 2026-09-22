#include "matrix.h"
#include "test-helpers.h"

#include <gtest/gtest.h>

namespace ct::test {

class ConstructorsTest : public ::testing::Test {
protected:
  void SetUp() override {
    Element::reset_allocations();
  }
};

TEST_F(ConstructorsTest, DefaultConstructor) {
  Matrix<Element> a;

  expect_empty(a);
  expect_allocations(0);
}

TEST_F(ConstructorsTest, ZerosConstructor) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t SIZE = ROWS * COLS;

  Matrix<Element> a(ROWS, COLS);

  EXPECT_EQ(a.rows(), ROWS);
  EXPECT_EQ(a.cols(), COLS);
  EXPECT_EQ(a.size(), SIZE);
  EXPECT_FALSE(a.empty());
  EXPECT_NE(a.data(), nullptr);

  for (std::size_t row_idx = 0; row_idx < ROWS; ++row_idx) {
    for (std::size_t col_idx = 0; col_idx < COLS; ++col_idx) {
      EXPECT_MATRIX_ELEM_EQ(a, row_idx, col_idx, 0);
    }
  }

  expect_allocations(SIZE);
}

TEST_F(ConstructorsTest, ZerosConstructorEmpty) {
  Matrix<Element> a(0, 0);

  expect_empty(a);
  expect_allocations(0);
}

TEST_F(ConstructorsTest, ZerosConstructorDegenerate) {
  Matrix<Element> a(10, 0);
  expect_empty(a);

  Matrix<Element> b(0, 10);
  expect_empty(b);

  expect_allocations(0);
}

TEST_F(ConstructorsTest, ArrayConstructor) {
  Matrix<Element> a({
      {10, 20, 30},
      {40, 50, 60},
  });

  EXPECT_EQ(a.rows(), 2);
  EXPECT_EQ(a.cols(), 3);
  EXPECT_EQ(a.size(), 6);
  EXPECT_FALSE(a.empty());
  EXPECT_NE(a.data(), nullptr);

  EXPECT_MATRIX_ELEM_EQ(a, 0, 0, 10);
  EXPECT_MATRIX_ELEM_EQ(a, 0, 1, 20);
  EXPECT_MATRIX_ELEM_EQ(a, 0, 2, 30);
  EXPECT_MATRIX_ELEM_EQ(a, 1, 0, 40);
  EXPECT_MATRIX_ELEM_EQ(a, 1, 1, 50);
  EXPECT_MATRIX_ELEM_EQ(a, 1, 2, 60);

  expect_allocations(6);
}

TEST_F(ConstructorsTest, CopyConstructor) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t SIZE = ROWS * COLS;

  Matrix<Element> a(ROWS, COLS);
  expect_allocations(SIZE);

  fill(a);
  expect_allocations(SIZE);

  Matrix<Element> b = a;

  expect_equal(b, a);
  expect_allocations(SIZE * 2);
}

TEST_F(ConstructorsTest, CopyConstructorEmpty) {
  Matrix<Element> a;
  Matrix<Element> b = a;

  expect_empty(a);
  expect_empty(b);

  expect_allocations(0);
}

TEST_F(ConstructorsTest, CopyAssignment) {
  constexpr std::size_t ROWS_A = 40;
  constexpr std::size_t COLS_A = 100;
  constexpr std::size_t SIZE_A = ROWS_A * COLS_A;

  constexpr std::size_t ROWS_B = 15;
  constexpr std::size_t COLS_B = 15;
  constexpr std::size_t SIZE_B = ROWS_B * COLS_B;

  Matrix<Element> b(ROWS_B, COLS_B);

  {
    Matrix<Element> a(ROWS_A, COLS_A);
    expect_allocations(SIZE_A + SIZE_B);

    fill(a);
    expect_allocations(SIZE_A + SIZE_B);

    b = a;
    expect_equal(b, a);
    expect_allocations(SIZE_A * 2 + SIZE_B);
  }

  for (std::size_t row_idx = 0; row_idx < ROWS_A; ++row_idx) {
    for (std::size_t col_idx = 0; col_idx < COLS_A; ++col_idx) {
      EXPECT_MATRIX_ELEM_EQ(b, row_idx, col_idx, elem(row_idx, col_idx));
    }
  }
}

TEST_F(ConstructorsTest, CopyAssignmentFromSelf) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t SIZE = ROWS * COLS;

  Matrix<Element> a(ROWS, COLS);
  expect_allocations(SIZE);

  fill(a);
  expect_allocations(SIZE);

  a = a;
  expect_allocations(SIZE);

  for (std::size_t row_idx = 0; row_idx < ROWS; ++row_idx) {
    for (std::size_t col_idx = 0; col_idx < COLS; ++col_idx) {
      EXPECT_MATRIX_ELEM_EQ(a, row_idx, col_idx, elem(row_idx, col_idx));
    }
  }
}

TEST_F(ConstructorsTest, CopyAssignmentFromEmpty) {
  constexpr std::size_t ROWS_B = 40;
  constexpr std::size_t COLS_B = 100;
  constexpr std::size_t SIZE_B = ROWS_B * COLS_B;

  Matrix<Element> a;
  Matrix<Element> b(ROWS_B, COLS_B);

  b = a;

  expect_empty(a);
  expect_empty(b);

  expect_allocations(SIZE_B);
}

} // namespace ct::test
