'use strict';

// zoneSurcharge는 export되지 않아 quoteShipping을 통해 검증한다.
// subtotal을 무료 배송 기준(50,000원) 이상으로 두면 기본 배송비가 0이 되어
// 결과가 지역 할증 금액과 같아진다.

const test = require('node:test');
const assert = require('node:assert/strict');
const { quoteShipping } = require('./shipping');

const FREE_SHIPPING_SUBTOTAL = 50000;

test('제주(63) 5kg 이하는 할증 3,000원', () => {
  const fee = quoteShipping({ postalCode: '63100', weightKg: 5, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 3000);
});

test('제주(63) 5kg 초과는 무게와 상관없이 할증 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5.1, subtotal: FREE_SHIPPING_SUBTOTAL }), 5000);
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 30, subtotal: FREE_SHIPPING_SUBTOTAL }), 5000);
});

test('23 지역 5kg 이하는 할증 3,000원', () => {
  const fee = quoteShipping({ postalCode: '23000', weightKg: 5, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 3000);
});

test('23 지역 5kg 초과분은 1kg 단위로 올림해 1kg당 1,000원 추가', () => {
  // 5.1kg -> 초과 0.1kg는 1kg로 올림
  const fee = quoteShipping({ postalCode: '23000', weightKg: 5.1, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 4000);
});

test('23 지역 정확히 정수 kg만큼 초과하면 올림 없이 그 kg만큼 추가', () => {
  const fee = quoteShipping({ postalCode: '23000', weightKg: 7, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 5000);
});

test('40 지역도 23 지역과 같은 무게별 할증을 받는다', () => {
  const fee = quoteShipping({ postalCode: '40500', weightKg: 6.5, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 5000);
});

test('할증 대상이 아닌 지역은 할증 0원', () => {
  const fee = quoteShipping({ postalCode: '06236', weightKg: 20, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 0);
});

test('우편번호 앞 두 자리로만 지역을 판단한다', () => {
  // 3으로 시작하지만 앞 두 자리가 '36'이므로 제주가 아니다
  const fee = quoteShipping({ postalCode: '36300', weightKg: 1, subtotal: FREE_SHIPPING_SUBTOTAL });
  assert.equal(fee, 0);
});

test('무료 배송 기준 미만이면 기본 배송비 3,000원에 할증이 더해진다', () => {
  const fee = quoteShipping({ postalCode: '63100', weightKg: 6, subtotal: 49999 });
  assert.equal(fee, 8000);
});
