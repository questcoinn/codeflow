import unittest

from pricing import apply_coupons


class MinimumOrderTest(unittest.TestCase):
    def test_order_of_9999_gets_no_discount(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}

        self.assertEqual(apply_coupons(9_999, [coupon]), 9_999)

    def test_order_of_exactly_10000_gets_discount(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}

        self.assertEqual(apply_coupons(10_000, [coupon]), 9_000)


class DiscountAmountTest(unittest.TestCase):
    def test_percent_coupon_takes_that_percent_off_the_order(self):
        coupon = {"type": "percent", "value": 10, "stackable": True}

        self.assertEqual(apply_coupons(50_000, [coupon]), 45_000)

    def test_percent_discount_drops_fraction_of_a_won(self):
        coupon = {"type": "percent", "value": 10, "stackable": True}

        # 10% of 10,005 is 1,000.5, so the discount is 1,000.
        self.assertEqual(apply_coupons(10_005, [coupon]), 9_005)

    def test_fixed_coupon_takes_its_amount_off_the_order(self):
        coupon = {"type": "fixed", "value": 3_000, "stackable": True}

        self.assertEqual(apply_coupons(50_000, [coupon]), 47_000)

    def test_stacked_percent_coupons_are_each_based_on_the_original_order(self):
        coupons = [
            {"type": "percent", "value": 10, "stackable": True},
            {"type": "percent", "value": 20, "stackable": True},
        ]

        # Applying them one after another would give 72,000.
        self.assertEqual(apply_coupons(100_000, coupons), 70_000)


class NonStackableCouponTest(unittest.TestCase):
    def test_non_stackable_coupon_combined_with_another_raises_error(self):
        coupons = [
            {"type": "fixed", "value": 1_000, "stackable": False},
            {"type": "fixed", "value": 1_000, "stackable": True},
        ]

        with self.assertRaises(ValueError):
            apply_coupons(50_000, coupons)

    def test_non_stackable_coupon_used_alone_is_applied(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": False}

        self.assertEqual(apply_coupons(50_000, [coupon]), 49_000)


class DiscountCapTest(unittest.TestCase):
    def test_discount_of_exactly_half_the_order_is_not_reduced(self):
        coupon = {"type": "percent", "value": 50, "stackable": True}

        self.assertEqual(apply_coupons(100_000, [coupon]), 50_000)

    def test_stacked_discount_over_half_the_order_is_capped_at_half(self):
        coupons = [
            {"type": "percent", "value": 30, "stackable": True},
            {"type": "percent", "value": 30, "stackable": True},
        ]

        self.assertEqual(apply_coupons(100_000, coupons), 50_000)

    def test_fixed_coupon_larger_than_the_order_is_capped_at_half(self):
        coupon = {"type": "fixed", "value": 30_000, "stackable": True}

        self.assertEqual(apply_coupons(20_000, [coupon]), 10_000)


if __name__ == "__main__":
    unittest.main()
