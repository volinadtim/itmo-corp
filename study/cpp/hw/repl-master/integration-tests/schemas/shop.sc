struct Product {
  uint32 id;
}

struct OrderItem {
  Product product;
  uint32 quantity;
}

fn getProduct -> Product {
  OrderItem item;
}

fn getQuantity -> uint32 {
  OrderItem item;
}

struct Order {
  uint32 id;
  OrderItem item;
}

fn addItemsToOrder -> Order {
  Order order;
  uint32 quantity;
}
