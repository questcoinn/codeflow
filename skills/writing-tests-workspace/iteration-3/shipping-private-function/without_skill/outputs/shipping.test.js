'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { quoteShipping } = require('./shipping');

// zoneSurcharge는 export되지 않은 내부 함수라서 공개 API인 quoteShipping을 통해 검증한다.
// subtotal을 무료 배송 기준(50000) 이상으로 주면 기본료가 0이 되므로
// quoteShipping의 반환값 == zoneSurcharge의 반환값이 된다.
const FREE = 50000;
const surcharge = (postalCode, weightKg) =>
  quoteShipping({ postalCode, weightKg, subtotal: FREE });

describe('zoneSurcharge (quoteShipping 경유, 기본료 0 조건)', () => {
  test('전제 확인: 무료 배송 기준 금액에서는 기본료가 0이다', () => {
    assert.equal(surcharge('12345', 1), 0);
    assert.equal(quoteShipping({ postalCode: '12345', weightKg: 1, subtotal: FREE - 1 }), 3000);
  });

  describe('63 지역 (5kg 기준 정액 2단계)', () => {
    const cases = [
      [0.1, 3000],
      [4.99, 3000],
      [5, 3000], // 경계: 5kg 이하
      [5.01, 5000], // 경계 바로 위
      [6, 5000],
      [30, 5000], // 무거워도 상한 5000 고정
    ];
    for (const [w, expected] of cases) {
      test(`63xxx, ${w}kg -> ${expected}`, () => {
        assert.equal(surcharge('63100', w), expected);
      });
    }
  });

  describe('23 / 40 지역 (3000 + 5kg 초과분 1kg당 1000, 올림)', () => {
    const cases = [
      [0.5, 3000],
      [5, 3000], // 경계: 초과분 0
      [5.01, 4000], // 조금만 넘어도 1kg으로 올림
      [5.5, 4000],
      [6, 4000], // 정확히 1kg 초과
      [6.01, 5000],
      [7, 5000],
      [10, 8000],
      [10.5, 9000],
    ];
    for (const prefix of ['23', '40']) {
      for (const [w, expected] of cases) {
        test(`${prefix}xxx, ${w}kg -> ${expected}`, () => {
          assert.equal(surcharge(`${prefix}000`, w), expected);
        });
      }
    }
  });

  describe('부동소수점 경계', () => {
    test('5.1kg (5.1 - 5 = 0.0999...) 는 1kg 초과로 올림', () => {
      assert.equal(surcharge('23456', 5.1), 4000);
    });
    test('6.000001kg 은 2kg 초과로 올림', () => {
      assert.equal(surcharge('40123', 6.000001), 5000);
    });
  });

  describe('할증 없는 지역', () => {
    for (const code of ['00000', '06234', '12345', '22999', '24000', '39999', '41000', '62999', '64000', '99999']) {
      test(`${code} -> 0 (무게와 무관)`, () => {
        assert.equal(surcharge(code, 1), 0);
        assert.equal(surcharge(code, 50), 0);
      });
    }
  });

  describe('앞 두 자리만 본다', () => {
    test('63 다음 자리와 무관하게 63 할증', () => {
      assert.equal(surcharge('63000', 1), 3000);
      assert.equal(surcharge('63999', 1), 3000);
    });
    test('뒤쪽에 63/23/40이 있어도 할증 없음', () => {
      assert.equal(surcharge('16300', 10), 0);
      assert.equal(surcharge('12340', 10), 0);
    });
  });

  describe('무료 배송이어도 할증은 붙는다 (기본료와 합산)', () => {
    test('무료 배송 + 63 지역 = 할증만', () => {
      assert.equal(quoteShipping({ postalCode: '63100', weightKg: 6, subtotal: FREE }), 5000);
    });
    test('유료 배송 + 23 지역 = 기본료 3000 + 할증', () => {
      assert.equal(quoteShipping({ postalCode: '23000', weightKg: 7, subtotal: 10000 }), 3000 + 5000);
    });
  });
});
