#include "socow-vector.h"
#include "test-utils.h"

#include <catch2/catch_test_macros.hpp>

#include <iterator>
#include <ranges>
#include <type_traits>

namespace ct_test {

TEST_CASE("Member types") {
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::ValueType, Element>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::Reference, Element&>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::ConstReference, const Element&>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::Pointer, Element*>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::ConstPointer, const Element*>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::Iterator, Element*>);
  STATIC_REQUIRE(std::is_same_v<ct::SocowVector<Element, 3>::ConstIterator, const Element*>);
}

TEST_CASE("SocowVector is contiguous") {
  STATIC_REQUIRE(std::contiguous_iterator<ct::SocowVector<Element, 3>::Iterator>);
  STATIC_REQUIRE(std::contiguous_iterator<ct::SocowVector<Element, 3>::ConstIterator>);

  STATIC_REQUIRE(std::ranges::contiguous_range<ct::SocowVector<Element, 3>>);
}

TEST_CASE("sizeof(SocowVector) is not too large") {
  STATIC_REQUIRE(sizeof(ct::SocowVector<void*, 10>) <= sizeof(void*) * 12);
  STATIC_REQUIRE(sizeof(ct::SocowVector<void*, 1>) <= sizeof(void*) * 3);
}

TEST_CASE("SocowVector is copyable and nothrow movable/swappable") {
  STATIC_REQUIRE(std::is_copy_constructible_v<ct::SocowVector<Element, 3>>);
  STATIC_REQUIRE(std::is_nothrow_move_constructible_v<ct::SocowVector<Element, 3>>);
  STATIC_REQUIRE(std::is_copy_assignable_v<ct::SocowVector<Element, 3>>);
  STATIC_REQUIRE(std::is_nothrow_move_assignable_v<ct::SocowVector<Element, 3>>);
  STATIC_REQUIRE(std::is_nothrow_swappable_v<ct::SocowVector<Element, 3>>);
}

} // namespace ct_test
