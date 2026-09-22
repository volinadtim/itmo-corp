#include "client.h"

#include <httplib.h>

#include <chrono>
#include <format>
#include <span>
#include <utility>

namespace ct::rpc {

namespace {

Client::Response
send_to_remote_server(const std::string& host, std::uint16_t port, const std::string& path, Client::Request request) {
  httplib::Client cli(host, port);
  cli.set_connection_timeout(std::chrono::seconds(1));

  auto response =
      cli.Post(path, reinterpret_cast<const char*>(request.data()), request.size(), "application/octet-stream");
  if (!response) {
    throw Exception("RPC response was not received");
  }

  switch (response->status) {
  case httplib::StatusCode::OK_200: {
    auto bytes = std::as_bytes(std::span(response->body));
    return {bytes.begin(), bytes.end()};
  }
  case httplib::StatusCode::BadRequest_400: {
    throw Exception(std::format("RPC error: {}", response->body));
  }
  default: {
    throw Exception(
        std::format("Unexpected server response (code: {}). Please report to the course staff.", response->status)
    );
  }
  }
}

} // namespace

Client::Client(std::string host, std::uint16_t port, std::string path)
    : _send_fn([host = std::move(host), port, path = std::move(path)](Request request) -> Response {
      return send_to_remote_server(host, port, path, request);
    }) {}

Client::Response Client::send(Request request) {
  return _send_fn(request);
}

} // namespace ct::rpc
