const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const { Cart } = require('./cart');

describe('Cart', () => {
  let cart;

  beforeEach(() => {
    cart = new Cart();
  });

  describe('add', () => {
    it('stores a new item with its price and quantity', () => {
      cart.add('apple', 100, 3);

      assert.deepEqual(cart.items.get('apple'), { price: 100, quantity: 3 });
    });

    it('defaults quantity to 1', () => {
      cart.add('apple', 100);

      assert.equal(cart.items.get('apple').quantity, 1);
    });

    it('accumulates quantity when the same sku is added again', () => {
      cart.add('apple', 100, 2);
      cart.add('apple', 100, 3);

      assert.equal(cart.items.size, 1);
      assert.equal(cart.items.get('apple').quantity, 5);
    });

    it('keeps different skus as separate items', () => {
      cart.add('apple', 100);
      cart.add('pear', 200);

      assert.equal(cart.items.size, 2);
    });

    // Pins current behavior: the price passed on a repeat add is ignored.
    it('keeps the original price when an existing sku is added at a new price', () => {
      cart.add('apple', 100, 1);
      cart.add('apple', 999, 1);

      assert.deepEqual(cart.items.get('apple'), { price: 100, quantity: 2 });
    });

    for (const quantity of [0, -1]) {
      it(`throws RangeError for quantity ${quantity}`, () => {
        assert.throws(() => cart.add('apple', 100, quantity), {
          name: 'RangeError',
          message: 'quantity must be positive',
        });
      });
    }

    it('leaves the cart unchanged when a new sku is rejected', () => {
      assert.throws(() => cart.add('apple', 100, 0), RangeError);

      assert.equal(cart.items.size, 0);
    });

    it('leaves an existing item unchanged when a repeat add is rejected', () => {
      cart.add('apple', 100, 2);

      assert.throws(() => cart.add('apple', 100, -1), RangeError);

      assert.equal(cart.items.get('apple').quantity, 2);
    });
  });

  describe('remove', () => {
    it('removes an existing item and returns true', () => {
      cart.add('apple', 100);

      assert.equal(cart.remove('apple'), true);
      assert.equal(cart.items.has('apple'), false);
    });

    it('returns false for an unknown sku', () => {
      assert.equal(cart.remove('missing'), false);
    });

    it('leaves other items in place', () => {
      cart.add('apple', 100);
      cart.add('pear', 200);

      cart.remove('apple');

      assert.equal(cart.items.has('pear'), true);
    });

    it('removes the whole line regardless of quantity', () => {
      cart.add('apple', 100, 5);

      cart.remove('apple');

      assert.equal(cart.total, 0);
    });
  });

  describe('total', () => {
    it('is 0 for an empty cart', () => {
      assert.equal(cart.total, 0);
    });

    it('multiplies price by quantity', () => {
      cart.add('apple', 100, 3);

      assert.equal(cart.total, 300);
    });

    it('sums across items', () => {
      cart.add('apple', 100, 2);
      cart.add('pear', 250, 3);

      assert.equal(cart.total, 950);
    });

    it('reflects accumulated quantity', () => {
      cart.add('apple', 100, 1);
      cart.add('apple', 100, 2);

      assert.equal(cart.total, 300);
    });

    it('drops when an item is removed', () => {
      cart.add('apple', 100, 2);
      cart.add('pear', 250);

      cart.remove('apple');

      assert.equal(cart.total, 250);
    });
  });

  it('does not share items between instances', () => {
    const other = new Cart();

    cart.add('apple', 100);

    assert.equal(other.items.size, 0);
  });
});
