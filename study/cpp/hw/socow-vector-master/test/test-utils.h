#pragma once

#include "element.h"
#include "socow-vector.h"

#include <catch2/catch_test_macros.hpp>

template class ct::SocowVector<int, 3>;
template class ct::SocowVector<ct_test::Element, 3>;
template class ct::SocowVector<ct_test::Element, 10>;

namespace ct_test {

template <typename... Ts>
class Snapshot {
public:
  explicit Snapshot(const Ts&... objects)
      : snapshots(objects...) {}

  Snapshot(const Snapshot&) = delete;

  void full_verify(const Ts&... objects) const {
    std::apply(
        [&](const Snapshot<Ts>&... snapshots) {
          (snapshots.full_verify(objects), ...);
        },
        snapshots
    );
  }

  void verify(const Ts&... objects) const {
    std::apply(
        [&](const Snapshot<Ts>&... snapshots) {
          (snapshots.verify(objects), ...);
        },
        snapshots
    );
  }

private:
  std::tuple<Snapshot<Ts>...> snapshots;
};

template <>
class Snapshot<Element> {
public:
  explicit Snapshot(const Element& e)
      : value(e) {}

  Snapshot(const Snapshot&) = delete;

  void full_verify(const Element& other) const {
    verify(other);
  }

  void verify(const Element& other) const {
    REQUIRE(value == other);
  }

  Element value;
};

template <std::size_t SMALL_SIZE>
class Snapshot<ct::SocowVector<Element, SMALL_SIZE>> {
public:
  explicit Snapshot(const ct::SocowVector<Element, SMALL_SIZE>& a)
      : capacity(a.capacity())
      , data(a.data())
      , elements(a.begin(), a.end()) {}

  Snapshot(const Snapshot&) = delete;

  void full_verify(const ct::SocowVector<Element, SMALL_SIZE>& other) const {
    REQUIRE(other.capacity() == capacity);
    REQUIRE(other.data() == data);
    verify(other);
  }

  void verify(const ct::SocowVector<Element, SMALL_SIZE>& other) const {
    REQUIRE(other.size() == elements.size());
    for (std::size_t i = 0; i < elements.size(); ++i) {
      CAPTURE(i);
      REQUIRE(other[i] == elements[i]);
    }
  }

  std::size_t capacity;
  const Element* data;
  std::vector<Element> elements;
};

template <std::size_t SMALL_SIZE>
bool is_static_storage(const ct::SocowVector<Element, SMALL_SIZE>& a) {
  if (a.capacity() != SMALL_SIZE) {
    return false;
  }
  const Element* data = a.data();
  return std::less_equal<const void*>{}(&a, data) && std::greater<const void*>{}(&a + 1, data);
}

template <std::size_t SMALL_SIZE>
void assert_empty_storage(const ct::SocowVector<Element, SMALL_SIZE>& a) {
  REQUIRE(a.empty());
  REQUIRE(a.size() == 0);
  REQUIRE(is_static_storage(a));
}

template <std::size_t SMALL_SIZE>
void mass_push_back(ct::SocowVector<Element, SMALL_SIZE>& a, std::size_t size) {
  for (std::size_t i = 0; i < size; ++i) {
    a.push_back(2 * i + 1);
  }
}

} // namespace ct_test
