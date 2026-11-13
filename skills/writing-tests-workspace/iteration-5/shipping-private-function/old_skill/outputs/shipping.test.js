'use strict';

// zoneSurcharge는 export되지 않아 quoteShipping을 통해 검증한다.
// subtotal을 무료 배송 기준(50,000원) 이상으로 두면 기본료가 0이 되어,
// 반환값이 곧 지역 할증 금액이다.

const test = require('node:test');
const assert = require('node:assert/strict');
const { quoteShipping } = require('./shipping');

const FREE = 50000;

// --- 63(제주) 지역: 5kg 이하 3,000원, 초과 5,000원 고정 ---

test('63 지역 5kg 정확히는 할증 3,000원', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5, subtotal: FREE }), 3000);
});

test('63 지역 5kg을 조금이라도 넘으면 할증 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5.1, subtotal: FREE }), 5000);
});

test('63 지역은 아주 무거워도 할증이 5,000원에서 늘지 않는다', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 30, subtotal: FREE }), 5000);
});

// --- 23/40 지역: 기본 3,000원 + 5kg 초과분을 kg 단위 올림해 1kg당 1,000원 ---

test('23 지역 5kg 이하는 할증 3,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 1, subtotal: FREE }), 3000);
});

test('23 지역 5kg 정확히는 추가 요금 없이 3,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 5, subtotal: FREE }), 3000);
});

test('23 지역 5kg을 0.1kg 넘으면 1kg으로 올림해 4,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 5.1, subtotal: FREE }), 4000);
});

test('23 지역 6.5kg은 초과분 1.5kg을 2kg으로 올림해 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 6.5, subtotal: FREE }), 5000);
});

test('23 지역 7kg은 초과분 2kg으로 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '23000', weightKg: 7, subtotal: FREE }), 5000);
});

test('40 지역도 23 지역과 같은 규칙으로 7kg이면 5,000원', () => {
  assert.equal(quoteShipping({ postalCode: '40000', weightKg: 7, subtotal: FREE }), 5000);
});

// --- 그 외 지역 ---

test('할증 대상이 아닌 지역은 할증 0원', () => {
  assert.equal(quoteShipping({ postalCode: '06000', weightKg: 30, subtotal: FREE }), 0);
});

test('우편번호 앞 두 자리로만 판정해 셋째 자리가 63이어도 할증 없음', () => {
  assert.equal(quoteShipping({ postalCode: '10630', weightKg: 1, subtotal: FREE }), 0);
});

// --- 기본료와의 합산 ---

test('무료 배송 기준 미만이면 기본료 3,000원에 할증이 더해진다', () => {
  assert.equal(quoteShipping({ postalCode: '63100', weightKg: 6, subtotal: 49999 }), 8000);
});
