import unittest

from inventory.stock import OutOfStock, Stock, release, reserve


class ReserveTest(unittest.TestCase):
    def test_reserving_adds_to_reserved_and_leaves_on_hand_unchanged(self):
        stock = Stock("APPLE", on_hand=10, reserved=2)

        result = reserve(stock, 3)

        self.assertEqual(result, Stock("APPLE", on_hand=10, reserved=5))

    def test_reserving_exactly_the_available_quantity_succeeds(self):
        stock = Stock("APPLE", on_hand=10, reserved=4)

        result = reserve(stock, 6)

        self.assertEqual(result.available, 0)

    def test_reserving_one_more_than_available_raises_out_of_stock(self):
        stock = Stock("APPLE", on_hand=10, reserved=4)

        with self.assertRaises(OutOfStock):
            reserve(stock, 7)

    def test_already_reserved_units_cannot_be_reserved_again(self):
        # on_hand 만으로는 충분해 보여도, 이미 예약된 7개는 가용 재고가 아니다.
        stock = Stock("APPLE", on_hand=10, reserved=7)

        with self.assertRaises(OutOfStock):
            reserve(stock, 4)

    def test_reserving_zero_raises_value_error(self):
        stock = Stock("APPLE", on_hand=10)

        with self.assertRaises(ValueError):
            reserve(stock, 0)

    def test_reserving_negative_quantity_raises_value_error(self):
        stock = Stock("APPLE", on_hand=10, reserved=5)

        with self.assertRaises(ValueError):
            reserve(stock, -3)


class ReleaseTest(unittest.TestCase):
    def test_releasing_subtracts_from_reserved(self):
        stock = Stock("APPLE", on_hand=10, reserved=5)

        result = release(stock, 2)

        self.assertEqual(result, Stock("APPLE", on_hand=10, reserved=3))

    def test_releasing_more_than_reserved_leaves_reserved_at_zero(self):
        stock = Stock("APPLE", on_hand=10, reserved=2)

        result = release(stock, 5)

        self.assertEqual(result.reserved, 0)

    def test_releasing_zero_raises_value_error(self):
        stock = Stock("APPLE", on_hand=10, reserved=5)

        with self.assertRaises(ValueError):
            release(stock, 0)


if __name__ == "__main__":
    unittest.main()
