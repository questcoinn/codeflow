'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { quoteShipping } = require('./shipping');

// zoneSurcharge는 export되지 않으므로 quoteShipping으로 검증한다.
// 주문 금액을 무료 배송 기준보다 넉넉히 높게(100,000원) 두면 기본 배송비가 0원이라, 결과가 곧 지역 할증이다.

test('제주(63) 5kg 이하는 할증 3,000원', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5, subtotal: 100000 }), 3000);
});

test('제주(63) 5kg를 조금이라도 넘으면 할증 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5.1, subtotal: 100000 }), 5000);
});

test('제주(63)는 무게가 아무리 늘어도 할증 5,000원에서 더 오르지 않는다', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 30, subtotal: 100000 }), 5000);
});

test('23 지역 5kg 이하는 할증 3,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 2, subtotal: 100000 }), 3000);
});

test('23 지역 5kg 초과분은 1kg 단위로 올림해 1kg당 1,000원 추가', () => {
  // 0.1kg 초과도 1kg로 친다
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 5.1, subtotal: 100000 }), 4000);
});

test('23 지역 7kg은 초과 2kg라 할증 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 7, subtotal: 100000 }), 5000);
});

test('40 지역도 23 지역과 같은 규칙으로 7.5kg은 할증 6,000원', () => {
  assert.equal(quoteShipping({ postalCode: '40200', weightKg: 7.5, subtotal: 100000 }), 6000);
});

test('할증 지역이 아니면 할증 0원', () => {
  assert.equal(quoteShipping({ postalCode: '06000', weightKg: 30, subtotal: 100000 }), 0);
});

test('우편번호 앞 두 자리만 본다: 셋째 자리가 63이어도 할증 없음', () => {
  assert.equal(quoteShipping({ postalCode: '06300', weightKg: 1, subtotal: 100000 }), 0);
});

test('무료 배송 기준 미만이면 기본 배송비 3,000원에 할증이 더해진다', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 1, subtotal: 49999 }), 6000);
});

test('무료 배송 기준(50,000원)을 채워도 지역 할증은 받는다', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 1, subtotal: 50000 }), 3000);
});
