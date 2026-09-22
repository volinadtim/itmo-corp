#include "typelist.h"

#include <catch2/catch_test_macros.hpp>

#include <tuple>
#include <type_traits>
#include <utility>

namespace ct_test::tl {

namespace tl = ct::tl;
using tl::TypeList;

template <typename... Types>
using Tuple = std::tuple<Types...>;

template <typename L, typename R>
using Pair = std::pair<L, R>;

TEST_CASE("contains") {
  STATIC_REQUIRE(tl::contains<int, TypeList<int, double, float>>);
  STATIC_REQUIRE(tl::contains<double, TypeList<int, double, float>>);
  STATIC_REQUIRE(tl::contains<float, TypeList<int, double, float>>);
  STATIC_REQUIRE(tl::contains<int, TypeList<int>>);
  STATIC_REQUIRE(tl::contains<int, TypeList<int, int>>);

  STATIC_REQUIRE(!tl::contains<char, TypeList<int, double, float>>);
  STATIC_REQUIRE(!tl::contains<char, TypeList<int>>);
  STATIC_REQUIRE(!tl::contains<char, TypeList<>>);
  STATIC_REQUIRE(!tl::contains<char, TypeList<int, int>>);

  STATIC_REQUIRE(tl::contains<int, Tuple<int, double, float>>);
  STATIC_REQUIRE(tl::contains<float, Tuple<int, double, float>>);
  STATIC_REQUIRE(tl::contains<int, Tuple<int>>);
  STATIC_REQUIRE(tl::contains<int, Tuple<int, int>>);

  STATIC_REQUIRE(!tl::contains<char, Tuple<int, double, float>>);
  STATIC_REQUIRE(!tl::contains<char, Tuple<int>>);
  STATIC_REQUIRE(!tl::contains<char, Tuple<>>);
  STATIC_REQUIRE(!tl::contains<char, Tuple<int, int>>);
}

TEST_CASE("flip_all") {
  STATIC_REQUIRE(std::is_same_v<tl::flip_all<TypeList<>>, TypeList<>>);
  STATIC_REQUIRE(std::is_same_v<tl::flip_all<Tuple<>>, Tuple<>>);

  using l11 = TypeList<TypeList<int, double>, TypeList<double, int>, TypeList<int, float>, TypeList<char, void>>;

  using l12 = TypeList<TypeList<double, int>, TypeList<int, double>, TypeList<float, int>, TypeList<void, char>>;

  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l11>, l12>);
  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l12>, l11>);

  // clang-format off
  using l21 = Tuple<
      TypeList<int, double>,
      TypeList<double, int>,
      Tuple<int, float>,
      TypeList<char, void>>;

  using l22 = Tuple<
      TypeList<double, int>,
      TypeList<int, double>,
      Tuple<float, int>,
      TypeList<void, char>>;
  // clang-format on

  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l21>, l22>);
  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l22>, l21>);

  using l31 = Pair<Pair<int, double>, Pair<long, float>>;
  using l32 = Pair<Pair<double, int>, Pair<float, long>>;

  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l31>, l32>);
  STATIC_REQUIRE(std::is_same_v<tl::flip_all<l32>, l31>);
}

TEST_CASE("index_of_unique") {
  STATIC_REQUIRE(tl::index_of_unique<int, TypeList<int, double, float>> == 0);
  STATIC_REQUIRE(tl::index_of_unique<double, TypeList<int, double, float>> == 1);
  STATIC_REQUIRE(tl::index_of_unique<float, TypeList<int, double, float>> == 2);
  STATIC_REQUIRE(tl::index_of_unique<int, TypeList<int>> == 0);

  STATIC_REQUIRE(tl::index_of_unique<int, Tuple<int, double, float>> == 0);
  STATIC_REQUIRE(tl::index_of_unique<double, Tuple<int, double, float>> == 1);
  STATIC_REQUIRE(tl::index_of_unique<float, Tuple<int, double, float>> == 2);
  STATIC_REQUIRE(tl::index_of_unique<int, Tuple<int>> == 0);
}

TEST_CASE("flatten") {
  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<int, double, float>>, TypeList<int, double, float>>);
  STATIC_REQUIRE(
      std::is_same_v<
          tl::flatten<TypeList<TypeList<int>, TypeList<double>, TypeList<float>>>,
          TypeList<int, double, float>>
  );
  STATIC_REQUIRE(
      std::is_same_v<tl::flatten<TypeList<int, TypeList<double>, TypeList<float>>>, TypeList<int, double, float>>
  );
  STATIC_REQUIRE(
      std::is_same_v<tl::flatten<TypeList<TypeList<int, TypeList<double>>, float>>, TypeList<int, double, float>>
  );
  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<>>, TypeList<>>);
  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<TypeList<TypeList<>>>>, TypeList<>>);

  STATIC_REQUIRE(std::is_same_v<tl::flatten<Tuple<int, double, float>>, Tuple<int, double, float>>);
  STATIC_REQUIRE(
      std::is_same_v<tl::flatten<Tuple<Tuple<int>, Tuple<double>, Tuple<float>>>, Tuple<int, double, float>>
  );
  STATIC_REQUIRE(
      std::is_same_v<tl::flatten<Tuple<TypeList<int>, TypeList<double>, TypeList<float>>>, Tuple<int, double, float>>
  );
  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<Tuple<int>, double, Tuple<float>>>, TypeList<int, double, float>>);

  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<Pair<int, int>, Pair<int, int>>>, TypeList<int, int, int, int>>);
  STATIC_REQUIRE(std::is_same_v<tl::flatten<TypeList<int, Pair<int, Pair<int, int>>>>, TypeList<int, int, int, int>>);
}

template <int N>
struct IntWrapper {};

template <template <typename...> typename List, int... Ns>
using make_int_list = List<IntWrapper<Ns>...>;

template <typename Lhs, typename Rhs>
struct LessCmp;

template <int LHS, int RHS>
struct LessCmp<IntWrapper<LHS>, IntWrapper<RHS>> {
  static constexpr bool value = LHS < RHS;
};

template <typename Lhs, typename Rhs, typename SomeParam = void>
struct Mod10GreaterCmp;

template <int LHS, int RHS>
struct Mod10GreaterCmp<IntWrapper<LHS>, IntWrapper<RHS>> {
  static constexpr bool value = LHS % 10 > RHS % 10;
};

TEST_CASE("merge_sort") {
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, TypeList<>>, TypeList<>>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, Tuple<>>, Tuple<>>);

  using l1 = make_int_list<TypeList, 42>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l1>, l1>);

  using l2 = make_int_list<TypeList, 42, 42>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l2>, l2>);

  using l3 = make_int_list<TypeList, 1, 0>;
  using l3_sorted = make_int_list<TypeList, 0, 1>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l3_sorted>, l3_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l3>, l3_sorted>);

  using l4 = make_int_list<TypeList, 2, 1, 3>;
  using l4_sorted = make_int_list<TypeList, 1, 2, 3>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l4_sorted>, l4_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l4>, l4_sorted>);

  using l5 = make_int_list<Tuple, 1, 3, 4, 2>;
  using l5_sorted = make_int_list<Tuple, 1, 2, 3, 4>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l5_sorted>, l5_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l5>, l5_sorted>);

  using l6 = make_int_list<Tuple, 5, 4, 3, 2, 1>;
  using l6_sorted = make_int_list<Tuple, 1, 2, 3, 4, 5>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l6_sorted>, l6_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l6>, l6_sorted>);

  using l7 = make_int_list<TypeList, 3, 7, 2, 9, 5>;
  using l7_sorted = make_int_list<TypeList, 2, 3, 5, 7, 9>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l7_sorted>, l7_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l7>, l7_sorted>);

  using l8 = make_int_list<TypeList, 2, 11, 7, 14, 18, 13, 6, 1, 1, 8, 5, 6, 8, 14, 15, 1>;
  using l8_sorted = make_int_list<TypeList, 1, 1, 1, 2, 5, 6, 6, 7, 8, 8, 11, 13, 14, 14, 15, 18>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l8_sorted>, l8_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<LessCmp, l8>, l8_sorted>);

  using l9 = make_int_list<TypeList, 12, 7, 14, 19, 13, 6, 1, 1, 8, 5, 6, 8, 14, 1>;
  using l9_sorted = make_int_list<TypeList, 19, 8, 8, 7, 6, 6, 5, 14, 14, 13, 12, 1, 1, 1>;
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<Mod10GreaterCmp, l9_sorted>, l9_sorted>);
  STATIC_REQUIRE(std::is_same_v<tl::merge_sort<Mod10GreaterCmp, l9>, l9_sorted>);
}

} // namespace ct_test::tl
