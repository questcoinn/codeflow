'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { quoteShipping } = require('./shipping');

// zoneSurcharge는 export되지 않아 quoteShipping을 통해 검증한다.
// subtotal을 무료 배송 기준(50,000원) 이상으로 두면 기본 배송비가 0이 되어
// 반환값이 곧 지역 할증 금액이다.
const FREE = 50000;

describe('zoneSurcharge: 우편번호 63으로 시작 (5kg 기준 정액)', () => {
  test('5kg 이하면 할증 3,000원', () => {
    assert.equal(quoteShipping({ postalCode: '63100', weightKg: 2, subtotal: FREE }), 3000);
  });

  test('정확히 5kg이면 아직 3,000원', () => {
    assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5, subtotal: FREE }), 3000);
  });

  test('5kg을 조금이라도 넘으면 5,000원', () => {
    assert.equal(quoteShipping({ postalCode: '63100', weightKg: 5.1, subtotal: FREE }), 5000);
  });

  test('무게가 많이 늘어도 5,000원에서 더 오르지 않는다', () => {
    assert.equal(quoteShipping({ postalCode: '63100', weightKg: 30, subtotal: FREE }), 5000);
  });
});

describe('zoneSurcharge: 우편번호 23·40으로 시작 (5kg 초과분 kg당 1,000원)', () => {
  test('23 지역 5kg 이하면 기본 할증 3,000원', () => {
    assert.equal(quoteShipping({ postalCode: '23000', weightKg: 3, subtotal: FREE }), 3000);
  });

  test('40 지역도 같은 규칙으로 5kg 이하면 3,000원', () => {
    assert.equal(quoteShipping({ postalCode: '40000', weightKg: 3, subtotal: FREE }), 3000);
  });

  test('정확히 5kg이면 초과분이 없어 3,000원', () => {
    assert.equal(quoteShipping({ postalCode: '23000', weightKg: 5, subtotal: FREE }), 3000);
  });

  test('5.1kg은 초과분 0.1kg을 1kg으로 올려 4,000원', () => {
    assert.equal(quoteShipping({ postalCode: '23000', weightKg: 5.1, subtotal: FREE }), 4000);
  });

  test('7kg은 초과분 2kg이라 5,000원', () => {
    assert.equal(quoteShipping({ postalCode: '40000', weightKg: 7, subtotal: FREE }), 5000);
  });

  test('6.5kg은 초과분 1.5kg을 2kg으로 올려 5,000원', () => {
    assert.equal(quoteShipping({ postalCode: '40000', weightKg: 6.5, subtotal: FREE }), 5000);
  });
});

describe('zoneSurcharge: 그 외 지역', () => {
  test('할증 대상이 아니면 할증 0원', () => {
    assert.equal(quoteShipping({ postalCode: '06000', weightKg: 20, subtotal: FREE }), 0);
  });

  test('앞자리가 아닌 위치에 63이 있어도 할증하지 않는다', () => {
    assert.equal(quoteShipping({ postalCode: '16300', weightKg: 3, subtotal: FREE }), 0);
  });
});

describe('quoteShipping: 기본 배송비와 할증의 합산', () => {
  test('무료 배송 기준 미만이면 기본 배송비 3,000원에 할증이 더해진다', () => {
    assert.equal(quoteShipping({ postalCode: '23000', weightKg: 7, subtotal: 49999 }), 8000);
  });
});
