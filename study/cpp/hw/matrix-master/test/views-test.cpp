#include "matrix.h"
#include "test-helpers.h"

#include <gtest/gtest.h>

namespace ct::test {

class ViewsTest : public ::testing::Test {
protected:
  void SetUp() override {
    Element::reset_allocations();
  }
};

TEST_F(ViewsTest, RowView) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_ROW = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  const Matrix<Element>::RowView row_view = a.row(CHOSEN_ROW);

  for (std::size_t i = 0; Element x : row_view) {
    const Element& expected = a[CHOSEN_ROW, i];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : row_view) {
    const Element& expected = a[CHOSEN_ROW, i];
    EXPECT_EQ(&x, &expected);
    ++i;
  }

  for (std::size_t i = 0; Element& x : row_view) {
    const Element& expected = a[CHOSEN_ROW, i];
    EXPECT_EQ(&x, &expected);
    x += 2;
    ++i;
  }

  for (std::size_t i = 0; Element x : a) {
    std::size_t row_idx = i / COLS;
    std::size_t col_idx = i % COLS;
    if (row_idx == CHOSEN_ROW) {
      EXPECT_EQ(x, elem(row_idx, col_idx) + 2);
    } else {
      EXPECT_EQ(x, elem(row_idx, col_idx));
    }
    ++i;
  }
}

TEST_F(ViewsTest, RowViewMultiply) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_ROW = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  const Matrix<Element>::RowView row_view = a.row(CHOSEN_ROW);

  (row_view *= 5) *= 2;

  for (std::size_t i = 0; Element x : a) {
    std::size_t row_idx = i / COLS;
    std::size_t col_idx = i % COLS;
    if (row_idx == CHOSEN_ROW) {
      EXPECT_EQ(x, elem(row_idx, col_idx) * 10);
    } else {
      EXPECT_EQ(x, elem(row_idx, col_idx));
    }
    ++i;
  }
}

TEST_F(ViewsTest, ConstRowView) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_ROW = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  Matrix<Element>::ConstRowView const_row_view = std::as_const(a).row(CHOSEN_ROW);

  for (std::size_t i = 0; Element x : const_row_view) {
    const Element& expected = a[CHOSEN_ROW, i];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : const_row_view) {
    const Element& expected = a[CHOSEN_ROW, i];
    EXPECT_EQ(&x, &expected);
    ++i;
  }
}

TEST_F(ViewsTest, ColView) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_COL = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  const Matrix<Element>::ColView col_view = a.col(CHOSEN_COL);

  for (std::size_t i = 0; Element x : col_view) {
    const Element& expected = a[i, CHOSEN_COL];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : col_view) {
    const Element& expected = a[i, CHOSEN_COL];
    EXPECT_EQ(&x, &expected);
    ++i;
  }

  for (std::size_t i = 0; Element& x : col_view) {
    const Element& expected = a[i, CHOSEN_COL];
    EXPECT_EQ(&x, &expected);
    x += 2;
    ++i;
  }

  for (std::size_t i = 0; Element x : a) {
    std::size_t row_idx = i / COLS;
    std::size_t col_idx = i % COLS;
    if (col_idx == CHOSEN_COL) {
      EXPECT_EQ(x, elem(row_idx, col_idx) + 2);
    } else {
      EXPECT_EQ(x, elem(row_idx, col_idx));
    }
    ++i;
  }
}

TEST_F(ViewsTest, ColViewMultiply) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_COL = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  const Matrix<Element>::ColView col_view = a.col(CHOSEN_COL);

  (col_view *= 5) *= 2;

  for (std::size_t i = 0; Element x : a) {
    std::size_t row_idx = i / COLS;
    std::size_t col_idx = i % COLS;
    if (col_idx == CHOSEN_COL) {
      EXPECT_EQ(x, elem(row_idx, col_idx) * 10);
    } else {
      EXPECT_EQ(x, elem(row_idx, col_idx));
    }
    ++i;
  }
}

TEST_F(ViewsTest, ConstColView) {
  constexpr std::size_t ROWS = 40;
  constexpr std::size_t COLS = 100;
  constexpr std::size_t CHOSEN_COL = 2;

  Matrix<Element> a(ROWS, COLS);
  fill(a);

  Matrix<Element>::ConstColView const_col_view = std::as_const(a).col(CHOSEN_COL);

  for (std::size_t i = 0; Element x : const_col_view) {
    const Element& expected = a[i, CHOSEN_COL];
    EXPECT_EQ(x, expected);
    ++i;
  }

  for (std::size_t i = 0; const Element& x : const_col_view) {
    const Element& expected = a[i, CHOSEN_COL];
    EXPECT_EQ(&x, &expected);
    ++i;
  }
}

} // namespace ct::test
