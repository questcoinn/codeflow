import unittest

from pricing import apply_coupons


class MinimumOrderTest(unittest.TestCase):
    def test_order_of_9_999_ignores_coupon(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}

        self.assertEqual(apply_coupons(9_999, [coupon]), 9_999)

    def test_order_of_exactly_10_000_gets_coupon(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}

        self.assertEqual(apply_coupons(10_000, [coupon]), 9_000)


class DiscountCalculationTest(unittest.TestCase):
    def test_percent_discount_drops_fraction_of_a_won(self):
        # 10,005원의 10%는 1,000.5원이므로 할인액은 1,000원이다.
        coupon = {"type": "percent", "value": 10, "stackable": True}

        self.assertEqual(apply_coupons(10_005, [coupon]), 9_005)

    def test_percent_coupon_after_fixed_coupon_uses_original_order_amount(self):
        # 정액 할인 후 금액(17,000원) 기준이면 할인액이 1,700원이 되어 15,300원이 나온다.
        fixed = {"type": "fixed", "value": 3_000, "stackable": True}
        percent = {"type": "percent", "value": 10, "stackable": True}

        self.assertEqual(apply_coupons(20_000, [fixed, percent]), 15_000)


class StackingTest(unittest.TestCase):
    def test_non_stackable_coupon_combined_with_another_raises(self):
        stackable = {"type": "fixed", "value": 1_000, "stackable": True}
        non_stackable = {"type": "fixed", "value": 1_000, "stackable": False}

        with self.assertRaises(ValueError):
            apply_coupons(20_000, [stackable, non_stackable])

    def test_non_stackable_coupon_used_alone_is_applied(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": False}

        self.assertEqual(apply_coupons(20_000, [coupon]), 19_000)


class DiscountCapTest(unittest.TestCase):
    def test_discount_of_exactly_50_percent_is_allowed(self):
        coupon = {"type": "percent", "value": 50, "stackable": True}

        self.assertEqual(apply_coupons(20_000, [coupon]), 10_000)

    def test_stacked_discounts_over_50_percent_are_capped_at_half_the_order(self):
        first = {"type": "percent", "value": 30, "stackable": True}
        second = {"type": "percent", "value": 30, "stackable": True}

        self.assertEqual(apply_coupons(20_000, [first, second]), 10_000)

    def test_fixed_coupon_larger_than_order_is_capped_at_half_the_order(self):
        coupon = {"type": "fixed", "value": 30_000, "stackable": True}

        self.assertEqual(apply_coupons(20_000, [coupon]), 10_000)


if __name__ == "__main__":
    unittest.main()
