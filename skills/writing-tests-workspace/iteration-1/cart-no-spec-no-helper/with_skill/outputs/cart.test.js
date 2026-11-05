const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Cart } = require('./cart');

test('빈 장바구니의 합계는 0이다', () => {
  const cart = new Cart();

  assert.equal(cart.total, 0);
});

test('합계는 상품별 가격 x 수량을 모두 더한 값이다', () => {
  const cart = new Cart();

  cart.add('apple', 1000, 2);
  cart.add('pear', 500, 3);

  assert.equal(cart.total, 3500);
});

test('수량을 생략하면 1개로 담긴다', () => {
  const cart = new Cart();

  cart.add('apple', 1000);

  assert.equal(cart.total, 1000);
});

test('같은 상품을 다시 담으면 수량이 누적된다', () => {
  const cart = new Cart();

  cart.add('apple', 1000, 2);
  cart.add('apple', 1000, 3);

  assert.equal(cart.total, 5000);
});

test('수량이 0이면 RangeError를 던진다', () => {
  const cart = new Cart();

  assert.throws(() => cart.add('apple', 1000, 0), RangeError);
});

test('수량이 음수이면 RangeError를 던진다', () => {
  const cart = new Cart();

  assert.throws(() => cart.add('apple', 1000, -1), RangeError);
});

test('잘못된 수량으로 담기에 실패해도 이미 담긴 수량은 그대로다', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);

  assert.throws(() => cart.add('apple', 1000, -1), RangeError);

  assert.equal(cart.total, 2000);
});

test('상품을 제거하면 그 상품만 합계에서 빠지고 true를 반환한다', () => {
  const cart = new Cart();
  cart.add('apple', 1000, 2);
  cart.add('pear', 500);

  const removed = cart.remove('apple');

  assert.equal(removed, true);
  assert.equal(cart.total, 500);
});

test('담기지 않은 상품을 제거하면 false를 반환하고 합계는 그대로다', () => {
  const cart = new Cart();
  cart.add('apple', 1000);

  const removed = cart.remove('pear');

  assert.equal(removed, false);
  assert.equal(cart.total, 1000);
});
