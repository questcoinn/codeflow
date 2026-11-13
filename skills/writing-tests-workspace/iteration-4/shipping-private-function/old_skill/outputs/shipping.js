'use strict';

const BASE_FEE = 3000;
const FREE_SHIPPING_THRESHOLD = 50000;

// 지역 할증. 무료 배송이어도 할증은 받는다.
function zoneSurcharge(postalCode, weightKg) {
  const prefix = postalCode.slice(0, 2);
  if (prefix === '63') {
    return weightKg <= 5 ? 3000 : 5000;
  }
  if (prefix === '23' || prefix === '40') {
    const extraKg = Math.max(0, Math.ceil(weightKg - 5));
    return 3000 + extraKg * 1000;
  }
  return 0;
}

function quoteShipping({ postalCode, weightKg, subtotal }) {
  if (!/^\d{5}$/.test(postalCode)) throw new TypeError('postalCode must be 5 digits');
  if (!(weightKg > 0)) throw new RangeError('weightKg must be positive');
  const base = subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : BASE_FEE;
  return base + zoneSurcharge(postalCode, weightKg);
}

module.exports = { quoteShipping };
