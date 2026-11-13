import unittest

from pricing import apply_coupons


class ApplyCouponsTest(unittest.TestCase):
    def test_order_below_10000_is_not_discounted(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]
        self.assertEqual(apply_coupons(9_999, coupons), 9_999)

    def test_order_of_exactly_10000_is_discounted(self):
        coupons = [{"type": "fixed", "value": 1_000, "stackable": True}]
        self.assertEqual(apply_coupons(10_000, coupons), 9_000)

    def test_percent_coupon_drops_fractional_won(self):
        # 10,010원의 15% = 1,501.5원 -> 1,501원만 할인
        coupons = [{"type": "percent", "value": 15, "stackable": True}]
        self.assertEqual(apply_coupons(10_010, coupons), 8_509)

    def test_fixed_coupon_subtracts_its_amount(self):
        coupons = [{"type": "fixed", "value": 3_000, "stackable": True}]
        self.assertEqual(apply_coupons(20_000, coupons), 17_000)

    def test_stackable_coupons_are_combined(self):
        coupons = [
            {"type": "percent", "value": 10, "stackable": True},
            {"type": "fixed", "value": 2_000, "stackable": True},
        ]
        self.assertEqual(apply_coupons(20_000, coupons), 16_000)

    def test_non_stackable_coupon_alone_is_applied(self):
        coupons = [{"type": "fixed", "value": 3_000, "stackable": False}]
        self.assertEqual(apply_coupons(20_000, coupons), 17_000)

    def test_non_stackable_coupon_with_another_coupon_raises(self):
        coupons = [
            {"type": "fixed", "value": 1_000, "stackable": False},
            {"type": "fixed", "value": 1_000, "stackable": True},
        ]
        with self.assertRaises(ValueError):
            apply_coupons(20_000, coupons)

    def test_discount_is_capped_at_half_of_order(self):
        coupons = [{"type": "fixed", "value": 15_000, "stackable": True}]
        self.assertEqual(apply_coupons(20_000, coupons), 10_000)

    def test_combined_discount_is_capped_at_half_of_order(self):
        coupons = [
            {"type": "percent", "value": 40, "stackable": True},
            {"type": "fixed", "value": 5_000, "stackable": True},
        ]
        self.assertEqual(apply_coupons(20_000, coupons), 10_000)


if __name__ == "__main__":
    unittest.main()
