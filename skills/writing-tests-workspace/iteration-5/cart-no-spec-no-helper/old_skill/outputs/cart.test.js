const test = require('node:test');
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

test('adding without a quantity adds one unit', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  assert.equal(cart.total, 1000);
});

test('adding an sku already in the cart increases its quantity', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('apple', 1000, 3);

  assert.equal(cart.total, 5000);
});

test('adding a quantity of 0 throws RangeError and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 1);

  assert.throws(() => cart.add('apple', 1000, 0), RangeError);
  assert.equal(cart.total, 1000);
});

test('adding a negative quantity throws RangeError and leaves the cart unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);

  assert.throws(() => cart.add('apple', 1000, -1), RangeError);
  assert.equal(cart.total, 2000);
});

test('removing an sku in the cart returns true and drops it from the total', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('pear', 2500, 1);

  assert.equal(cart.remove('apple'), true);
  assert.equal(cart.total, 2500);
});

test('removing an sku not in the cart returns false and leaves the total unchanged', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);

  assert.equal(cart.remove('pear'), false);
  assert.equal(cart.total, 2000);
});
