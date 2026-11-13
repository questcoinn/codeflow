const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Cart } = require('./cart');

test('an empty cart totals 0', () => {
  const cart = new Cart();

  assert.equal(cart.total, 0);
});

test('adding an item without a quantity counts it once', () => {
  const cart = new Cart();

  cart.add('apple', 1000);

  assert.equal(cart.total, 1000);
});

test('total is the sum of price times quantity across all items', () => {
  const cart = new Cart();

  cart.add('apple', 1000, 3);
  cart.add('pear', 2500, 2);

  assert.equal(cart.total, 8000);
});

test('adding the same sku again increases its quantity', () => {
  const cart = new Cart();

  cart.add('apple', 1000, 2);
  cart.add('apple', 1000, 3);

  assert.equal(cart.total, 5000);
});

test('adding a quantity of 0 throws RangeError and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  assert.throws(() => cart.add('apple', 1000, 0), RangeError);
  assert.equal(cart.total, 1000);
});

test('adding a negative quantity throws RangeError and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  assert.throws(() => cart.add('apple', 1000, -1), RangeError);
  assert.equal(cart.total, 1000);
});

test('removing an item in the cart returns true and drops it from the total', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('pear', 2500);

  const removed = cart.remove('apple');

  assert.equal(removed, true);
  assert.equal(cart.total, 2500);
});

test('removing a sku not in the cart returns false', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  const removed = cart.remove('pear');

  assert.equal(removed, false);
  assert.equal(cart.total, 1000);
});
