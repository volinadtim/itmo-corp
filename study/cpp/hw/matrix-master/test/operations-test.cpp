#include "matrix.h"
#include "test-helpers.h"

#include <gtest/gtest.h>

#include <numeric>

namespace ct::test {

class OperationsTest : public ::testing::Test {
protected:
  void SetUp() override {
    Element::reset_allocations();
  }
};

TEST_F(OperationsTest, ElementAccess) {
  Matrix<Element> a(2, 3);

  a[0, 2] = 5;
  a[1, 1] = 42;
  a[1, 2] = a[0, 2];

  const Matrix<Element>& ca = a;

  EXPECT_MATRIX_ELEM_EQ(ca, 0, 0, 0);
  EXPECT_MATRIX_ELEM_EQ(ca, 0, 1, 0);
  EXPECT_MATRIX_ELEM_EQ(ca, 0, 2, 5);
  EXPECT_MATRIX_ELEM_EQ(ca, 1, 0, 0);
  EXPECT_MATRIX_ELEM_EQ(ca, 1, 1, 42);
  EXPECT_MATRIX_ELEM_EQ(ca, 1, 2, 5);
}

TEST_F(OperationsTest, Data) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  {
    Element* data = a.data();
    for (std::size_t row_idx = 0; row_idx < ROWS; ++row_idx) {
      for (std::size_t col_idx = 0; col_idx < COLS; ++col_idx) {
        EXPECT_EQ(data[row_idx * COLS + col_idx], elem(row_idx, col_idx));
      }
    }
  }

  {
    const Element* data = std::as_const(a).data();
    for (std::size_t row_idx = 0; row_idx < ROWS; ++row_idx) {
      for (std::size_t col_idx = 0; col_idx < COLS; ++col_idx) {
        EXPECT_EQ(data[row_idx * COLS + col_idx], elem(row_idx, col_idx));
      }
    }
  }
}

TEST_F(OperationsTest, RangeBasedFor) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  for (std::size_t i = 0; Element x : a) {
    Element expected = a[i / COLS, i % COLS];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; Element x : std::as_const(a)) {
    Element expected = a[i / COLS, i % COLS];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : a) {
    EXPECT_EQ(&x, a.data() + i);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : std::as_const(a)) {
    EXPECT_EQ(&x, a.data() + i);
    ++i;
  }

  for (std::size_t i = 0; Element& x : a) {
    EXPECT_EQ(&x, a.data() + i);
    x += 2;
    ++i;
  }

  for (std::size_t i = 0; Element x : a) {
    EXPECT_EQ(x, elem(i / COLS, i % COLS) + 2);
    ++i;
  }
}

TEST_F(OperationsTest, Compare) {
  Matrix<Element> a({
      {10, 20, 30},
      {40, 50, 60},
  });
  Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });
  Matrix<Element> c({
      {10, 20, 30},
      {42, 50, 60},
  });
  Matrix<Element> d({
      {10, 20},
      {30, 40},
      {50, 60},
  });
  Matrix<Element> e({
      {10, 20, 30},
  });
  Matrix<Element> f({
      {{10}},
      {{40}},
  });

  EXPECT_TRUE(a == b);
  EXPECT_FALSE(a != b);

  EXPECT_TRUE(a != c);
  EXPECT_FALSE(a == c);

  EXPECT_TRUE(a != d);
  EXPECT_FALSE(a == d);

  EXPECT_TRUE(a != e);
  EXPECT_FALSE(a == e);

  EXPECT_TRUE(a != f);
  EXPECT_FALSE(a == f);
}

TEST_F(OperationsTest, CompareEmpty) {
  Matrix<Element> a, b;
  EXPECT_TRUE(a == b);
  EXPECT_FALSE(a != b);

  expect_allocations(0);
}

TEST_F(OperationsTest, Add) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });
  const Matrix<Element> c({
      {11, 22, 33},
      {44, 55, 66},
  });

  std::size_t expected_allocations = a.size() + b.size() + c.size();

  expect_equal(std::as_const(a) + b, c);
  expect_allocations(expected_allocations += c.size() * 2);

  a += b;
  expect_equal(a, c);
  expect_allocations(expected_allocations);
}

TEST_F(OperationsTest, AddReturnValue) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });
  const Matrix<Element> c({
      {21, 42, 63},
      {84, 105, 126},
  });

  (a += b) += b;
  expect_equal(a, c);
  expect_allocations(a.size() + b.size() + c.size());
}

TEST_F(OperationsTest, AddEmpty) {
  Matrix<Element> a;
  Matrix<Element> b;

  expect_empty(a + b);

  a += b;
  expect_empty(a);
  expect_allocations(0);
}

TEST_F(OperationsTest, AddSelf) {
  Matrix<Element> a({
      {1, 2},
      {3, 4},
  });
  const Matrix<Element> expected = a * 2;

  a += a;
  expect_equal(a, expected);
}

TEST_F(OperationsTest, Subtract) {
  Matrix<Element> a({
      {11, 22, 33},
      {44, 55, 66},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });
  const Matrix<Element> c({
      {1, 2, 3},
      {4, 5, 6},
  });

  std::size_t expected_allocations = a.size() + b.size() + c.size();

  expect_equal(std::as_const(a) - b, c);
  expect_allocations(expected_allocations += c.size() * 2);

  a -= b;
  expect_equal(a, c);
  expect_allocations(expected_allocations);
}

TEST_F(OperationsTest, SubtractReturnValue) {
  Matrix<Element> a({
      {21, 42, 63},
      {84, 105, 126},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });
  const Matrix<Element> c({
      {1, 2, 3},
      {4, 5, 6},
  });

  (a -= b) -= b;
  expect_equal(a, c);
  expect_allocations(a.size() + b.size() + c.size());
}

TEST_F(OperationsTest, SubtractEmpty) {
  Matrix<Element> a;
  Matrix<Element> b;

  expect_empty(a - b);

  a -= b;
  expect_empty(a);
  expect_allocations(0);
}

TEST_F(OperationsTest, SubtractSelf) {
  Matrix<Element> a({
      {1, 2},
      {3, 4},
  });
  const Matrix<Element> expected = a * 0;

  a -= a;
  expect_equal(a, expected);
}

TEST_F(OperationsTest, MultiplyMatrix) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
      {7, 8, 9},
  });
  const Matrix<Element> b({
      {10, 40},
      {20, 50},
      {30, 60},
  });
  const Matrix<Element> c({
      {140, 320},
      {320, 770},
      {500, 1220},
  });

  std::size_t expected_allocations = a.size() + b.size() + c.size();

  expect_equal(std::as_const(a) * b, c);
  expect_allocations(expected_allocations += c.size());

  a *= b;
  expect_equal(a, c);
  expect_allocations(expected_allocations += c.size());
}

TEST_F(OperationsTest, MultiplyMatrixReturnValue) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
      {7, 8, 9},
  });
  const Matrix<Element> b({
      {10, 40},
      {20, 50},
      {30, 60},
  });
  const Matrix<Element> c({
      {150, 360},
      {340, 820},
      {530, 1280},
  });

  std::size_t expected_allocations = a.size() + b.size() + c.size();

  (a *= b) += b;
  expect_equal(a, c);
  expect_allocations(expected_allocations += c.size());
}

TEST_F(OperationsTest, MultiplyMatrixEmpty) {
  Matrix<Element> a;
  Matrix<Element> b;

  expect_empty(a * b);

  a *= b;
  expect_empty(a);
  expect_allocations(0);
}

TEST_F(OperationsTest, MultiplyMatrixSelf) {
  Matrix<Element> a({
      {1, 2},
      {3, 4},
  });
  const Matrix<Element> expected({
      {7, 10},
      {15, 22},
  });

  a *= a;
  expect_equal(a, expected);
}

TEST_F(OperationsTest, MultiplyScalar) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });

  std::size_t expected_allocations = a.size() + b.size();

  expect_equal(std::as_const(a) * 10, b);
  expect_equal(10 * std::as_const(a), b);
  expect_allocations(expected_allocations += b.size() * 4);

  a *= 10;
  expect_equal(a, b);
  expect_allocations(expected_allocations);
}

TEST_F(OperationsTest, MultiplyScalarReturnValue) {
  Matrix<Element> a({
      {1, 2, 3},
      {4, 5, 6},
  });
  const Matrix<Element> b({
      {10, 20, 30},
      {40, 50, 60},
  });

  (a *= 5) *= 2;
  expect_equal(a, b);
  expect_allocations(a.size() + b.size());
}

TEST_F(OperationsTest, MultiplyScalarEmpty) {
  Matrix<Element> a;

  expect_empty(std::as_const(a) * 10);
  expect_empty(10 * std::as_const(a));

  a *= 10;
  expect_empty(a);
  expect_allocations(0);
}

} // namespace ct::test
