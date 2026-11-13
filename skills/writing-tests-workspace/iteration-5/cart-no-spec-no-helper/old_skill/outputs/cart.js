class Cart {
  constructor() {
    this.items = new Map();
  }

  add(sku, price, quantity = 1) {
    if (quantity <= 0) throw new RangeError('quantity must be positive');
    const item = this.items.get(sku);
    if (item) item.quantity += quantity;
    else this.items.set(sku, { price, quantity });
  }

  remove(sku) {
    return this.items.delete(sku);
  }

  get total() {
    let sum = 0;
    for (const { price, quantity } of this.items.values()) sum += price * quantity;
    return sum;
  }
}

module.exports = { Cart };
