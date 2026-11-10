import unittest

from pricing import apply_coupons


class MinimumOrderTest(unittest.TestCase):
    def test_orders_under_10000_ignore_coupons(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}
        self.assertEqual(apply_coupons(9_999, [coupon]), 9_999)

    def test_orders_of_exactly_10000_get_coupons(self):
        coupon = {"type": "fixed", "value": 1_000, "stackable": True}
        self.assertEqual(apply_coupons(10_000, [coupon]), 9_000)


class DiscountTypeTest(unittest.TestCase):
    def test_percent_coupon_discounts_by_rate_and_drops_fractional_won(self):
        # 12,347 * 10% = 1,234.7 -> 1,234 discount (not rounded up to 1,235)
        coupon = {"type": "percent", "value": 10, "stackable": True}
        self.assertEqual(apply_coupons(12_347, [coupon]), 11_113)

    def test_fixed_coupon_discounts_by_its_amount(self):
        coupon = {"type": "fixed", "value": 3_000, "stackable": True}
        self.assertEqual(apply_coupons(20_000, [coupon]), 17_000)


class StackingTest(unittest.TestCase):
    def test_stackable_coupons_add_their_discounts(self):
        percent = {"type": "percent", "value": 10, "stackable": True}
        fixed = {"type": "fixed", "value": 1_000, "stackable": True}
        self.assertEqual(apply_coupons(20_000, [percent, fixed]), 17_000)

    def test_non_stackable_coupon_combined_with_another_raises(self):
        exclusive = {"type": "fixed", "value": 1_000, "stackable": False}
        other = {"type": "fixed", "value": 1_000, "stackable": True}
        with self.assertRaises(ValueError):
            apply_coupons(20_000, [exclusive, other])

    def test_non_stackable_coupon_used_alone_is_applied(self):
        exclusive = {"type": "fixed", "value": 1_000, "stackable": False}
        self.assertEqual(apply_coupons(20_000, [exclusive]), 19_000)


class DiscountCapTest(unittest.TestCase):
    def test_stacked_discounts_are_capped_at_half_the_order(self):
        # 40% + 30% would be 14,000 off; cap is 10,000
        first = {"type": "percent", "value": 40, "stackable": True}
        second = {"type": "percent", "value": 30, "stackable": True}
        self.assertEqual(apply_coupons(20_000, [first, second]), 10_000)

    def test_fixed_coupon_larger_than_order_is_capped_at_half_the_order(self):
        coupon = {"type": "fixed", "value": 30_000, "stackable": True}
        self.assertEqual(apply_coupons(20_000, [coupon]), 10_000)


if __name__ == "__main__":
    unittest.main()
