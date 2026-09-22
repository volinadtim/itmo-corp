#pragma once

#include <cstddef>

namespace ct {

template <typename T>
class Matrix {
public:
  using ValueType = T;

  using Reference = T&;
  using ConstReference = const T&;

  using Pointer = T*;
  using ConstPointer = const T*;

  using Iterator = void;
  using ConstIterator = void;

  using RowIterator = void;
  using ConstRowIterator = void;

  using ColIterator = void;
  using ConstColIterator = void;

  using RowView = void;
  using ConstRowView = void;

  using ColView = void;
  using ConstColView = void;

public:
  Matrix();

  Matrix(std::size_t n_rows, std::size_t n_cols);

  template <std::size_t ROWS, std::size_t COLS>
  Matrix(const T (&init)[ROWS][COLS]);

  Matrix(const Matrix& other);

  Matrix& operator=(const Matrix& other);

  ~Matrix();

  // Iterators

  Iterator begin();
  ConstIterator begin() const;
  Iterator end();
  ConstIterator end() const;

  RowIterator row_begin(std::size_t row_idx);
  ConstRowIterator row_begin(std::size_t row_idx) const;
  RowIterator row_end(std::size_t row_idx);
  ConstRowIterator row_end(std::size_t row_idx) const;

  ColIterator col_begin(std::size_t col_idx);
  ConstColIterator col_begin(std::size_t col_idx) const;
  ColIterator col_end(std::size_t col_idx);
  ConstColIterator col_end(std::size_t col_idx) const;

  // Views

  RowView row(std::size_t row_idx);
  ConstRowView row(std::size_t row_idx) const;

  ColView col(std::size_t col_idx);
  ConstColView col(std::size_t col_idx) const;

  // Size

  std::size_t rows() const;
  std::size_t cols() const;
  std::size_t size() const;
  bool empty() const;

  // Elements access

  Reference operator[](std::size_t row_idx, std::size_t col_idx);
  ConstReference operator[](std::size_t row_idx, std::size_t col_idx) const;

  Pointer data();
  ConstPointer data() const;

  // Comparison

  friend bool operator==(const Matrix& lhs, const Matrix& rhs);
  friend bool operator!=(const Matrix& lhs, const Matrix& rhs);

  // Arithmetic operations

  Matrix& operator+=(const Matrix& other);
  Matrix& operator-=(const Matrix& other);
  Matrix& operator*=(const Matrix& other);
  Matrix& operator*=(ConstReference factor);

  friend Matrix operator+(const Matrix& lhs, const Matrix& rhs);
  friend Matrix operator-(const Matrix& lhs, const Matrix& rhs);
  friend Matrix operator*(const Matrix& lhs, const Matrix& rhs);
  friend Matrix operator*(const Matrix& lhs, ConstReference rhs);
  friend Matrix operator*(ConstReference lhs, const Matrix& rhs);
};

} // namespace ct
