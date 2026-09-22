#include "matrix.h"
#include "test-helpers.h"

#include <gtest/gtest.h>

namespace ct::test {

#define EXPECT_TRAIT(...) EXPECT_TRUE((__VA_ARGS__))

TEST(TraitsTest, MemberTypes) {
  EXPECT_TRAIT(std::is_same_v<Element, Matrix<Element>::ValueType>);

  EXPECT_TRAIT(std::is_same_v<Element&, Matrix<Element>::Reference>);
  EXPECT_TRAIT(std::is_same_v<const Element&, Matrix<Element>::ConstReference>);

  EXPECT_TRAIT(std::is_same_v<Element*, Matrix<Element>::Pointer>);
  EXPECT_TRAIT(std::is_same_v<const Element*, Matrix<Element>::ConstPointer>);

  EXPECT_TRAIT(std::is_same_v<Element*, Matrix<Element>::Iterator>);
  EXPECT_TRAIT(std::is_same_v<const Element*, Matrix<Element>::ConstIterator>);

  EXPECT_TRAIT(std::is_same_v<Element*, Matrix<Element>::RowIterator>);
  EXPECT_TRAIT(std::is_same_v<const Element*, Matrix<Element>::ConstRowIterator>);
}

TEST(TraitsTest, IteratorCategories) {
  EXPECT_TRAIT(std::contiguous_iterator<Matrix<Element>::Iterator>);
  EXPECT_TRAIT(std::contiguous_iterator<Matrix<Element>::ConstIterator>);

  EXPECT_TRAIT(std::contiguous_iterator<Matrix<Element>::RowIterator>);
  EXPECT_TRAIT(std::contiguous_iterator<Matrix<Element>::ConstRowIterator>);

  EXPECT_TRAIT(std::random_access_iterator<Matrix<Element>::ColIterator>);
  EXPECT_TRAIT(std::random_access_iterator<Matrix<Element>::ConstColIterator>);
}

TEST(TraitsTest, RangeCategories) {
  EXPECT_TRAIT(std::ranges::contiguous_range<Matrix<Element>>);
  EXPECT_TRAIT(std::ranges::contiguous_range<const Matrix<Element>>);

  EXPECT_TRAIT(std::ranges::contiguous_range<Matrix<Element>::RowView>);
  EXPECT_TRAIT(std::ranges::contiguous_range<Matrix<Element>::ConstRowView>);

  EXPECT_TRAIT(std::ranges::random_access_range<Matrix<Element>::ColView>);
  EXPECT_TRAIT(std::ranges::random_access_range<Matrix<Element>::ConstColView>);
}

TEST(TraitsTest, ColIteratorMemberTypes) {
  using ColIteratorTraits = std::iterator_traits<Matrix<Element>::ColIterator>;
  using ConstColIteratorTraits = std::iterator_traits<Matrix<Element>::ConstColIterator>;

  EXPECT_TRAIT(std::is_same_v<Element, ColIteratorTraits::value_type>);
  EXPECT_TRAIT(std::is_same_v<Element&, ColIteratorTraits::reference>);
  EXPECT_TRAIT(std::is_same_v<Element*, ColIteratorTraits::pointer>);
  EXPECT_TRAIT(std::is_same_v<std::ptrdiff_t, ColIteratorTraits::difference_type>);
  EXPECT_TRAIT(std::is_same_v<std::random_access_iterator_tag, ColIteratorTraits::iterator_category>);

  EXPECT_TRAIT(std::is_same_v<Element, ConstColIteratorTraits::value_type>);
  EXPECT_TRAIT(std::is_same_v<const Element&, ConstColIteratorTraits::reference>);
  EXPECT_TRAIT(std::is_same_v<const Element*, ConstColIteratorTraits::pointer>);
  EXPECT_TRAIT(std::is_same_v<std::ptrdiff_t, ConstColIteratorTraits::difference_type>);
  EXPECT_TRAIT(std::is_same_v<std::random_access_iterator_tag, ConstColIteratorTraits::iterator_category>);
}

TEST(TraitsTest, IteratorTriviality) {
  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::Iterator>);
  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::ConstIterator>);

  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::RowIterator>);
  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::ConstRowIterator>);

  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::ColIterator>);
  EXPECT_TRAIT(std::is_trivial_v<Matrix<Element>::ConstColIterator>);
}

} // namespace ct::test
