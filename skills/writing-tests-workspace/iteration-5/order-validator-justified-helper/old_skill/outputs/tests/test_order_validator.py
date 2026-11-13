import unittest
from datetime import date

from src.order_validator import Order, validate


def make_valid_order(**overrides):
    """모든 검증을 통과하는 주문. 테스트에서 확인할 필드만 overrides로 바꾼다."""
    fields = dict(
        order_id="O-1",
        customer_id="C-1",
        customer_email="buyer@example.com",
        shipping_name="홍길동",
        shipping_phone="010-0000-0000",
        shipping_address="서울시 어딘가",
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
        self.assertEqual(validate(make_valid_order()), [])

    def test_bank_transfer_is_an_accepted_payment_method(self):
        order = make_valid_order(payment_method="bank_transfer")
        self.assertEqual(validate(order), [])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_invalid(self):
        order = make_valid_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_with_four_digits_is_invalid(self):
        order = make_valid_order(shipping_zip="1234")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_zip_with_six_digits_is_invalid(self):
        order = make_valid_order(shipping_zip="123456")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_five_character_zip_with_non_digit_is_invalid(self):
        order = make_valid_order(shipping_zip="1234A")
        self.assertEqual(validate(order), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_of_zero_is_invalid(self):
        order = make_valid_order(item_quantity=0)
        self.assertEqual(validate(order), ["invalid_quantity"])

    def test_quantity_of_99_is_the_maximum_allowed(self):
        order = make_valid_order(item_quantity=99)
        self.assertEqual(validate(order), [])

    def test_quantity_of_100_is_invalid(self):
        order = make_valid_order(item_quantity=100)
        self.assertEqual(validate(order), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_price_of_zero_is_allowed(self):
        order = make_valid_order(unit_price=0)
        self.assertEqual(validate(order), [])

    def test_negative_price_is_invalid(self):
        order = make_valid_order(unit_price=-1)
        self.assertEqual(validate(order), ["invalid_price"])


class PaymentMethodTest(unittest.TestCase):
    def test_unsupported_payment_method_is_invalid(self):
        order = make_valid_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_on_the_order_date_is_invalid(self):
        order = make_valid_order(
            ordered_on=date(2026, 1, 1), delivery_on=date(2026, 1, 1)
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_the_order_date_is_invalid(self):
        order = make_valid_order(
            ordered_on=date(2026, 1, 1), delivery_on=date(2025, 12, 31)
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])


class MultipleErrorsTest(unittest.TestCase):
    def test_every_violated_rule_is_reported_together(self):
        order = make_valid_order(customer_email="no-at-sign", item_quantity=0)
        self.assertCountEqual(
            validate(order), ["invalid_email", "invalid_quantity"]
        )


if __name__ == "__main__":
    unittest.main()
