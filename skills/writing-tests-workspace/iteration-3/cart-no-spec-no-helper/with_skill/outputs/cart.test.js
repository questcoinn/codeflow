const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Cart } = require('./cart');

test('an empty cart totals 0', () => {
  const cart = new Cart();

  assert.equal(cart.total, 0);
});

test('total is the sum of price times quantity across all items', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 3);
  cart.add('pear', 2500, 2);

  assert.equal(cart.total, 8000);
});

test('add without a quantity adds one unit', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  assert.equal(cart.total, 1000);
});

test('adding the same sku again increases its quantity instead of replacing it', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('apple', 1000, 3);

  assert.equal(cart.total, 5000);
});

test('add rejects a quantity of 0 and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 1);

  assert.throws(() => cart.add('apple', 1000, 0), RangeError);
  assert.equal(cart.total, 1000);
});

test('add rejects a negative quantity and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);

  assert.throws(() => cart.add('apple', 1000, -1), RangeError);
  assert.equal(cart.total, 2000);
});

test('remove drops the item from the total and returns true', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('pear', 2500, 1);

  assert.equal(cart.remove('apple'), true);
  assert.equal(cart.total, 2500);
});

test('remove returns false for a sku that is not in the cart', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 1);

  assert.equal(cart.remove('pear'), false);
  assert.equal(cart.total, 1000);
});
