"""apply_coupons 테스트. 기대값의 기준은 구현이 아니라 docs/coupon-spec.md 이다.

실행: python -m unittest -v
"""
import unittest

from pricing import apply_coupons


def percent(value, stackable=True):
    return {"type": "percent", "value": value, "stackable": stackable}


def fixed(value, stackable=True):
    return {"type": "fixed", "value": value, "stackable": stackable}


class MinimumOrderTest(unittest.TestCase):
    """스펙 2: 주문 금액이 10,000원 미만이면 쿠폰을 적용하지 않는다."""

    def test_just_below_minimum_ignores_coupon(self):
        self.assertEqual(apply_coupons(9_999, [percent(10)]), 9_999)

    def test_exactly_minimum_applies_coupon(self):
        self.assertEqual(apply_coupons(10_000, [percent(10)]), 9_000)


class DiscountCalculationTest(unittest.TestCase):
    """스펙 3, 4: 정률/정액 할인 계산."""

    def test_percent_discount(self):
        self.assertEqual(apply_coupons(20_000, [percent(10)]), 18_000)

    def test_percent_discount_truncates_below_one_won(self):
        # 10,005 * 15% = 1,500.75 -> 할인액 1,500 (반올림이면 1,501)
        self.assertEqual(apply_coupons(10_005, [percent(15)]), 8_505)

    def test_fixed_discount(self):
        self.assertEqual(apply_coupons(20_000, [fixed(3_000)]), 17_000)

    def test_stacked_percents_are_based_on_order_amount(self):
        # 순차 적용이면 16,200 이 된다. 스펙 3은 "주문 금액의 비율"이다.
        self.assertEqual(apply_coupons(20_000, [percent(10), percent(10)]), 16_000)

    def test_percent_and_fixed_stack(self):
        self.assertEqual(apply_coupons(20_000, [percent(10), fixed(1_000)]), 17_000)


class FinalAmountFloorTest(unittest.TestCase):
    """스펙 5: 최종 금액은 0원 미만이 될 수 없다."""

    def test_fixed_coupon_larger_than_order_does_not_go_negative(self):
        # 정확한 금액은 스펙 7이 정하므로 여기서는 하한만 확인한다.
        self.assertGreaterEqual(apply_coupons(15_000, [fixed(20_000)]), 0)


class StackabilityTest(unittest.TestCase):
    """스펙 6: 중복 불가 쿠폰은 다른 쿠폰과 함께 쓰면 오류가 난다."""

    def test_non_stackable_coupon_alone_is_allowed(self):
        self.assertEqual(apply_coupons(20_000, [percent(10, stackable=False)]), 18_000)

    def test_non_stackable_with_stackable_raises(self):
        for coupons in (
            [fixed(1_000, stackable=False), percent(10)],
            [percent(10), fixed(1_000, stackable=False)],
        ):
            with self.subTest(coupons=coupons):
                with self.assertRaises(ValueError):
                    apply_coupons(20_000, coupons)

    def test_two_non_stackable_coupons_raise(self):
        with self.assertRaises(ValueError):
            apply_coupons(20_000, [percent(10, stackable=False), fixed(1_000, stackable=False)])


class DiscountCapTest(unittest.TestCase):
    """스펙 7: 총 할인액은 주문 금액의 50%를 넘을 수 없다."""

    def test_discount_of_exactly_half_is_allowed(self):
        self.assertEqual(apply_coupons(20_000, [percent(50)]), 10_000)

    def test_single_percent_coupon_is_capped(self):
        self.assertEqual(apply_coupons(20_000, [percent(60)]), 10_000)

    def test_single_fixed_coupon_is_capped(self):
        self.assertEqual(apply_coupons(20_000, [fixed(15_000)]), 10_000)

    def test_stacked_coupons_are_capped_on_their_sum(self):
        # 쿠폰 하나하나는 50% 이하지만 합계가 넘는 경우
        self.assertEqual(apply_coupons(20_000, [percent(30), fixed(8_000)]), 10_000)

    def test_fixed_coupon_larger_than_order_is_capped(self):
        self.assertEqual(apply_coupons(15_000, [fixed(20_000)]), 7_500)


class LoggingTest(unittest.TestCase):
    """스펙 8, 9: "pricing" 로거로 "coupon applied" 로 시작하는 INFO 로그를 남긴다."""

    def test_applied_coupon_logs_info_on_module_logger(self):
        with self.assertLogs("pricing", level="INFO") as logs:
            apply_coupons(20_000, [percent(10)])

        self.assertEqual(len(logs.records), 1)
        self.assertEqual(logs.records[0].levelname, "INFO")
        self.assertTrue(logs.records[0].getMessage().startswith("coupon applied"))

    def test_no_log_when_coupon_is_not_applied(self):
        with self.assertNoLogs("pricing", level="INFO"):
            apply_coupons(9_999, [percent(10)])


if __name__ == "__main__":
    unittest.main()
