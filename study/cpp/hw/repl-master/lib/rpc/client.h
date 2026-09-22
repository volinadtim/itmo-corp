#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace ct::rpc {

class Exception : public std::runtime_error {
public:
  using std::runtime_error::runtime_error;
};

class Client {
public:
  using Response = std::vector<std::byte>;
  using Request = std::span<const std::byte>;
  using SendFn = std::function<Response(Request)>;

  Client(std::string host, std::uint16_t port, std::string path);

  template <typename TSendFn>
    requires std::convertible_to<TSendFn, SendFn>
  explicit Client(TSendFn&& send_fn)
      : _send_fn(std::forward<TSendFn>(send_fn)) {}

  Response send(Request request);

private:
  SendFn _send_fn;
};

} // namespace ct::rpc
