import unittest

from pricing import apply_coupons


class ApplyCouponsTest(unittest.TestCase):
    def test_order_below_10000_is_returned_without_discount(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]

        self.assertEqual(apply_coupons(9_999, coupons), 9_999)

    def test_order_of_exactly_10000_gets_coupon(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]

        self.assertEqual(apply_coupons(10_000, coupons), 9_000)

    def test_percent_coupon_discounts_by_rate_of_order(self):
        coupons = [{"type": "percent", "value": 10, "stackable": True}]

        self.assertEqual(apply_coupons(20_000, coupons), 18_000)

    def test_percent_coupon_drops_fraction_of_a_won_from_discount(self):
        # 10% of 10,005 is 1,000.5 -> discount 1,000
        coupons = [{"type": "percent", "value": 10, "stackable": True}]

        self.assertEqual(apply_coupons(10_005, coupons), 9_005)

    def test_stackable_coupons_add_up(self):
        coupons = [
            {"type": "percent", "value": 10, "stackable": True},
            {"type": "fixed", "value": 3_000, "stackable": True},
        ]

        self.assertEqual(apply_coupons(20_000, coupons), 15_000)

    def test_non_stackable_coupon_alone_is_applied(self):
        coupons = [{"type": "fixed", "value": 2_000, "stackable": False}]

        self.assertEqual(apply_coupons(20_000, coupons), 18_000)

    def test_non_stackable_coupon_combined_with_another_raises(self):
        coupons = [
            {"type": "fixed", "value": 1_000, "stackable": False},
            {"type": "fixed", "value": 1_000, "stackable": True},
        ]

        with self.assertRaises(ValueError):
            apply_coupons(20_000, coupons)

    def test_total_discount_is_capped_at_half_of_order(self):
        coupons = [
            {"type": "percent", "value": 40, "stackable": True},
            {"type": "fixed", "value": 5_000, "stackable": True},
        ]

        self.assertEqual(apply_coupons(20_000, coupons), 10_000)

    def test_fixed_coupon_larger_than_order_is_still_capped_at_half(self):
        coupons = [{"type": "fixed", "value": 30_000, "stackable": True}]

        self.assertEqual(apply_coupons(20_000, coupons), 10_000)


if __name__ == "__main__":
    unittest.main()
