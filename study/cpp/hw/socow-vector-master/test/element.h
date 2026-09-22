#pragma once

#include <ostream>
#include <set>

namespace ct_test {

struct Element {
  struct NoNewInstancesGuard;

  Element() = delete;
  Element(int data);
  Element(const Element& other);
  Element(Element&& other) noexcept;
  ~Element();

  Element& operator=(const Element& other);
  Element& operator=(Element&& other) noexcept;

  friend bool operator==(const Element& lhs, const Element& rhs);
  friend bool operator!=(const Element& lhs, const Element& rhs);

  friend std::ostream& operator<<(std::ostream& out, const Element& e);

private:
  void add_instance();
  void delete_instance();
  void assert_exists() const;

private:
  int value;

  inline static std::set<const Element*> instances;
};

struct Element::NoNewInstancesGuard {
  NoNewInstancesGuard();

  NoNewInstancesGuard(const NoNewInstancesGuard&) = delete;
  NoNewInstancesGuard& operator=(const NoNewInstancesGuard&) = delete;

  ~NoNewInstancesGuard() noexcept(false);

  bool check_no_new_instances() const noexcept;

private:
  std::set<const Element*> old_instances;
};

} // namespace ct_test
