#include "element.h"

#include <catch2/catch_test_macros.hpp>

#include <utility>

namespace ct_test {

Element::Element(int data)
    : value(data) {
  add_instance();
}

Element::Element(const Element& other)
    : value(-1) {
  other.assert_exists();
  add_instance();
  value = other.value;
}

Element::Element(Element&& other) noexcept
    : value(-1) {
  other.assert_exists();
  add_instance();
  value = std::exchange(other.value, -1);
}

Element::~Element() {
  delete_instance();
}

Element& Element::operator=(const Element& other) {
  assert_exists();
  other.assert_exists();

  value = other.value;
  return *this;
}

Element& Element::operator=(Element&& other) noexcept {
  assert_exists();
  other.assert_exists();

  value = std::exchange(other.value, -1);
  return *this;
}

bool operator==(const Element& lhs, const Element& rhs) {
  lhs.assert_exists();
  rhs.assert_exists();

  return lhs.value == rhs.value;
}

bool operator!=(const Element& lhs, const Element& rhs) {
  return !(lhs == rhs);
}

std::ostream& operator<<(std::ostream& out, const Element& e) {
  e.assert_exists();
  out << e.value;
  return out;
}

void Element::add_instance() {
  auto p = instances.insert(this);
  if (!p.second) {
    // clang-format off
    FAIL(
        "A new object is created at the address "
        << static_cast<void*>(this)
        << " while the previous object at this address was not destroyed"
    );
    // clang-format on
  }
}

void Element::delete_instance() {
  std::size_t erased = instances.erase(this);
  if (erased != 1) {
    FAIL("Attempt of destroying non-existing object at address " << static_cast<void*>(this));
  }
}

void Element::assert_exists() const {
  bool exists = instances.find(this) != instances.end();
  if (!exists) {
    FAIL("Accessing a non-existing object at address " << static_cast<const void*>(this));
  }
}

Element::NoNewInstancesGuard::NoNewInstancesGuard()
    : old_instances(instances) {}

Element::NoNewInstancesGuard::~NoNewInstancesGuard() noexcept(false) {
  if (std::uncaught_exceptions() == 0) {
    bool no_new_instances = check_no_new_instances();
    instances = old_instances;
    REQUIRE(no_new_instances);
  } else {
    instances = old_instances;
  }
}

bool Element::NoNewInstancesGuard::check_no_new_instances() const noexcept {
  return old_instances == instances;
}

} // namespace ct_test
