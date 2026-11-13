import unittest
from datetime import date

from src.order_validator import Order, validate


def make_order(**overrides):
    """모든 검증을 통과하는 주문을 만든다. 테스트할 필드만 인자로 바꿔 넘긴다."""
    fields = dict(
        order_id="O-1",
        customer_id="C-1",
        customer_email="buyer@example.com",
        shipping_name="홍길동",
        shipping_phone="010-0000-0000",
        shipping_address="서울시 어딘가 1",
        shipping_zip="12345",
        item_sku="SKU-1",
        item_quantity=1,
        unit_price=1000,
        payment_method="card",
        ordered_on=date(2026, 1, 1),
        delivery_on=date(2026, 1, 2),
    )
    fields.update(overrides)
    return Order(**fields)


class ValidOrderTest(unittest.TestCase):
    def test_valid_order_has_no_errors(self):
        self.assertEqual(validate(make_order()), [])

    def test_all_errors_are_reported_together(self):
        order = make_order(customer_email="no-at-sign", item_quantity=0)
        self.assertCountEqual(validate(order), ["invalid_email", "invalid_quantity"])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_invalid(self):
        order = make_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_four_digit_zip_is_invalid(self):
        self.assertEqual(validate(make_order(shipping_zip="1234")), ["invalid_zip"])

    def test_six_digit_zip_is_invalid(self):
        self.assertEqual(validate(make_order(shipping_zip="123456")), ["invalid_zip"])

    def test_five_character_zip_with_non_digit_is_invalid(self):
        self.assertEqual(validate(make_order(shipping_zip="1234a")), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_1_is_allowed(self):
        self.assertEqual(validate(make_order(item_quantity=1)), [])

    def test_quantity_99_is_allowed(self):
        self.assertEqual(validate(make_order(item_quantity=99)), [])

    def test_quantity_0_is_invalid(self):
        self.assertEqual(validate(make_order(item_quantity=0)), ["invalid_quantity"])

    def test_quantity_100_is_invalid(self):
        self.assertEqual(validate(make_order(item_quantity=100)), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_zero_price_is_allowed(self):
        self.assertEqual(validate(make_order(unit_price=0)), [])

    def test_negative_price_is_invalid(self):
        self.assertEqual(validate(make_order(unit_price=-1)), ["invalid_price"])


class PaymentMethodTest(unittest.TestCase):
    def test_bank_transfer_is_allowed(self):
        self.assertEqual(validate(make_order(payment_method="bank_transfer")), [])

    def test_unsupported_payment_method_is_invalid(self):
        order = make_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_on_the_order_date_is_invalid(self):
        order = make_order(ordered_on=date(2026, 1, 1), delivery_on=date(2026, 1, 1))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_the_order_date_is_invalid(self):
        order = make_order(ordered_on=date(2026, 1, 2), delivery_on=date(2026, 1, 1))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_the_day_after_ordering_is_allowed(self):
        order = make_order(ordered_on=date(2026, 1, 1), delivery_on=date(2026, 1, 2))
        self.assertEqual(validate(order), [])


if __name__ == "__main__":
    unittest.main()
