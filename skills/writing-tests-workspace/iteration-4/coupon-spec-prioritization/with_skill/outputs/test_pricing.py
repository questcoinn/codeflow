import unittest

from pricing import apply_coupons


class ApplyCouponsTest(unittest.TestCase):
    def test_order_below_10000_is_not_discounted(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]

        self.assertEqual(apply_coupons(9_999, coupons), 9_999)

    def test_order_of_exactly_10000_is_discounted(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]

        self.assertEqual(apply_coupons(10_000, coupons), 9_000)

    def test_fixed_coupon_subtracts_its_amount(self):
        coupons = [{"type": "fixed", "value": 3_000, "stackable": False}]

        self.assertEqual(apply_coupons(20_000, coupons), 17_000)

    def test_percent_coupon_drops_fractions_of_a_won_from_the_discount(self):
        # 10,009원의 10%는 1,000.9원이므로 할인액은 1,000원이다.
        coupons = [{"type": "percent", "value": 10, "stackable": False}]

        self.assertEqual(apply_coupons(10_009, coupons), 9_009)

    def test_stackable_coupons_are_combined(self):
        coupons = [
            {"type": "percent", "value": 10, "stackable": True},
            {"type": "fixed", "value": 1_000, "stackable": True},
        ]

        self.assertEqual(apply_coupons(20_000, coupons), 17_000)

    def test_non_stackable_coupon_combined_with_another_raises_error(self):
        coupons = [
            {"type": "fixed", "value": 1_000, "stackable": False},
            {"type": "fixed", "value": 1_000, "stackable": True},
        ]

        with self.assertRaises(ValueError):
            apply_coupons(20_000, coupons)

    def test_total_discount_is_capped_at_half_of_the_order(self):
        coupons = [{"type": "fixed", "value": 15_000, "stackable": False}]

        self.assertEqual(apply_coupons(20_000, coupons), 10_000)

    def test_combined_discount_is_capped_at_half_of_the_order(self):
        coupons = [
            {"type": "percent", "value": 30, "stackable": True},
            {"type": "percent", "value": 30, "stackable": True},
        ]

        self.assertEqual(apply_coupons(20_000, coupons), 10_000)


if __name__ == "__main__":
    unittest.main()
