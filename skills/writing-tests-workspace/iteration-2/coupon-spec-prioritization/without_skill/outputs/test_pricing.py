"""docs/coupon-spec.md 기준 apply_coupons 테스트. 실행: python -m unittest -v"""
import unittest

import pricing
from pricing import apply_coupons


def percent(value, stackable=True):
    return {"type": "percent", "value": value, "stackable": stackable}


def fixed(value, stackable=True):
    return {"type": "fixed", "value": value, "stackable": stackable}


class MinimumOrderTest(unittest.TestCase):
    """스펙 2: 10,000원 미만이면 쿠폰을 적용하지 않는다."""

    def test_below_minimum_ignores_coupon(self):
        self.assertEqual(apply_coupons(9_999, [fixed(1_000)]), 9_999)

    def test_exactly_minimum_applies_coupon(self):
        self.assertEqual(apply_coupons(10_000, [fixed(1_000)]), 9_000)


class DiscountCalculationTest(unittest.TestCase):
    """스펙 3, 4: 정률/정액 할인 계산."""

    def test_percent_discounts_by_rate(self):
        self.assertEqual(apply_coupons(20_000, [percent(10)]), 18_000)

    def test_percent_discount_truncates_below_one_won(self):
        # 할인액 1,234.5원 -> 1,234원. 결과를 버림하면 11,110원이 되어 틀린다.
        self.assertEqual(apply_coupons(12_345, [percent(10)]), 11_111)

    def test_fixed_discounts_by_amount(self):
        self.assertEqual(apply_coupons(20_000, [fixed(3_000)]), 17_000)

    def test_stacked_percents_are_based_on_order_amount(self):
        # 순차 적용이면 16,200원이 된다.
        self.assertEqual(apply_coupons(20_000, [percent(10), percent(10)]), 16_000)

    def test_stacked_result_does_not_depend_on_coupon_order(self):
        self.assertEqual(apply_coupons(20_000, [percent(10), fixed(3_000)]), 15_000)
        self.assertEqual(apply_coupons(20_000, [fixed(3_000), percent(10)]), 15_000)

    def test_no_coupons_keeps_order_amount(self):
        self.assertEqual(apply_coupons(20_000, []), 20_000)


class FinalAmountFloorTest(unittest.TestCase):
    """스펙 5: 최종 금액은 0원 미만이 될 수 없다."""

    def test_oversized_discount_does_not_go_negative(self):
        self.assertGreaterEqual(apply_coupons(20_000, [fixed(999_999)]), 0)


class DiscountCapTest(unittest.TestCase):
    """스펙 7: 총 할인액은 주문 금액의 50%를 넘을 수 없다."""

    def test_discount_of_exactly_half_is_allowed(self):
        self.assertEqual(apply_coupons(20_000, [fixed(10_000)]), 10_000)

    def test_fixed_discount_one_won_over_half_is_capped(self):
        self.assertEqual(apply_coupons(20_000, [fixed(10_001)]), 10_000)

    def test_fixed_discount_over_order_amount_is_capped(self):
        self.assertEqual(apply_coupons(20_000, [fixed(30_000)]), 10_000)

    def test_percent_discount_over_half_is_capped(self):
        self.assertEqual(apply_coupons(20_000, [percent(60)]), 10_000)

    def test_stacked_discount_over_half_is_capped(self):
        # 쿠폰 하나하나는 50% 이하여도 합계에 상한이 걸린다.
        self.assertEqual(apply_coupons(20_000, [percent(30), fixed(8_000)]), 10_000)


class StackingTest(unittest.TestCase):
    """스펙 6: 중복 불가 쿠폰을 함께 쓰면 오류가 난다."""

    def test_non_stackable_with_stackable_raises_in_either_order(self):
        with self.assertRaises(ValueError):
            apply_coupons(20_000, [fixed(1_000, stackable=False), fixed(1_000)])
        with self.assertRaises(ValueError):
            apply_coupons(20_000, [fixed(1_000), fixed(1_000, stackable=False)])

    def test_two_non_stackable_raises(self):
        with self.assertRaises(ValueError):
            apply_coupons(
                20_000,
                [fixed(1_000, stackable=False), percent(10, stackable=False)],
            )

    def test_non_stackable_alone_is_applied(self):
        self.assertEqual(apply_coupons(20_000, [fixed(1_000, stackable=False)]), 19_000)


class LoggingTest(unittest.TestCase):
    """스펙 8, 9: 적용 시 INFO 로그, 로거 이름은 모듈 이름."""

    def test_applied_coupon_logs_info_on_module_logger(self):
        with self.assertLogs(pricing.__name__, level="INFO") as logs:
            apply_coupons(20_000, [fixed(1_000)])

        self.assertEqual(len(logs.records), 1)
        record = logs.records[0]
        self.assertEqual(record.name, pricing.__name__)
        self.assertEqual(record.levelname, "INFO")
        self.assertTrue(record.getMessage().startswith("coupon applied"))

    def test_no_log_when_coupon_is_not_applied(self):
        with self.assertNoLogs(pricing.__name__, level="INFO"):
            apply_coupons(9_999, [fixed(1_000)])


if __name__ == "__main__":
    unittest.main()
