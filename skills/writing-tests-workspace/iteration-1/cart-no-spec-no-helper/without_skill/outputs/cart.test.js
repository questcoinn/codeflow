const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { Cart } = require('./cart.js');

describe('Cart', () => {
  describe('total', () => {
    it('빈 장바구니는 0이다', () => {
      assert.equal(new Cart().total, 0);
    });

    it('여러 상품의 가격 x 수량을 합산한다', () => {
      const cart = new Cart();
      cart.add('apple', 100, 2);
      cart.add('pear', 250, 3);

      assert.equal(cart.total, 950);
    });
  });

  describe('add', () => {
    it('수량을 생략하면 1개로 담는다', () => {
      const cart = new Cart();
      cart.add('apple', 100);

      assert.equal(cart.total, 100);
    });

    it('같은 sku를 다시 담으면 수량이 누적된다', () => {
      const cart = new Cart();
      cart.add('apple', 100, 2);
      cart.add('apple', 100, 3);

      assert.equal(cart.total, 500);
      assert.equal(cart.items.size, 1);
    });

    for (const quantity of [0, -1]) {
      it(`수량이 ${quantity}이면 RangeError를 던지고 담지 않는다`, () => {
        const cart = new Cart();

        assert.throws(() => cart.add('apple', 100, quantity), {
          name: 'RangeError',
          message: 'quantity must be positive',
        });
        assert.equal(cart.items.size, 0);
      });
    }

    it('잘못된 수량으로 실패해도 이미 담긴 상품은 그대로다', () => {
      const cart = new Cart();
      cart.add('apple', 100, 2);

      assert.throws(() => cart.add('apple', 100, -1), RangeError);
      assert.equal(cart.total, 200);
    });
  });

  describe('remove', () => {
    it('담긴 상품을 제거하면 true를 반환하고 합계에서 빠진다', () => {
      const cart = new Cart();
      cart.add('apple', 100, 2);
      cart.add('pear', 250);

      assert.equal(cart.remove('apple'), true);
      assert.equal(cart.total, 250);
    });

    it('없는 sku를 제거하면 false를 반환하고 나머지는 그대로다', () => {
      const cart = new Cart();
      cart.add('apple', 100);

      assert.equal(cart.remove('pear'), false);
      assert.equal(cart.total, 100);
    });

    it('제거 후 다시 담으면 이전 수량이 이어지지 않는다', () => {
      const cart = new Cart();
      cart.add('apple', 100, 5);
      cart.remove('apple');
      cart.add('apple', 100);

      assert.equal(cart.total, 100);
    });
  });

  it('장바구니 인스턴스끼리 상태를 공유하지 않는다', () => {
    const first = new Cart();
    const second = new Cart();
    first.add('apple', 100);

    assert.equal(second.total, 0);
  });
});
