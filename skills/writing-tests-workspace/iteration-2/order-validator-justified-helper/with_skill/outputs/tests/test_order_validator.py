import unittest
from datetime import date

from src.order_validator import Order, validate


def make_valid_order(**overrides):
    """유효한 주문을 만든다. 테스트에서 중요한 필드는 인자로 넘겨 드러낸다."""
    fields = {
        "order_id": "order-1",
        "customer_id": "customer-1",
        "customer_email": "buyer@example.com",
        "shipping_name": "홍길동",
        "shipping_phone": "010-1234-5678",
        "shipping_address": "서울시 중구 세종대로 110",
        "shipping_zip": "04524",
        "item_sku": "sku-1",
        "item_quantity": 1,
        "unit_price": 10_000,
        "payment_method": "card",
        "ordered_on": date(2026, 1, 1),
        "delivery_on": date(2026, 1, 3),
    }
    return Order(**{**fields, **overrides})


class ValidOrderTest(unittest.TestCase):
    def test_order_with_all_valid_fields_has_no_errors(self):
        self.assertEqual(validate(make_valid_order()), [])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_rejected(self):
        order = make_valid_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_shorter_than_5_digits_is_rejected(self):
        order = make_valid_order(shipping_zip="0452")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_zip_longer_than_5_digits_is_rejected(self):
        order = make_valid_order(shipping_zip="045240")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_5_character_zip_with_non_digit_is_rejected(self):
        order = make_valid_order(shipping_zip="0452A")
        self.assertEqual(validate(order), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_0_is_rejected(self):
        order = make_valid_order(item_quantity=0)
        self.assertEqual(validate(order), ["invalid_quantity"])

    def test_quantity_1_is_accepted(self):
        order = make_valid_order(item_quantity=1)
        self.assertEqual(validate(order), [])

    def test_quantity_99_is_accepted(self):
        order = make_valid_order(item_quantity=99)
        self.assertEqual(validate(order), [])

    def test_quantity_100_is_rejected(self):
        order = make_valid_order(item_quantity=100)
        self.assertEqual(validate(order), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_negative_price_is_rejected(self):
        order = make_valid_order(unit_price=-1)
        self.assertEqual(validate(order), ["invalid_price"])

    def test_price_0_is_accepted(self):
        order = make_valid_order(unit_price=0)
        self.assertEqual(validate(order), [])


class PaymentMethodTest(unittest.TestCase):
    def test_card_is_accepted(self):
        order = make_valid_order(payment_method="card")
        self.assertEqual(validate(order), [])

    def test_bank_transfer_is_accepted(self):
        order = make_valid_order(payment_method="bank_transfer")
        self.assertEqual(validate(order), [])

    def test_unknown_payment_method_is_rejected(self):
        order = make_valid_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_the_day_after_ordering_is_accepted(self):
        order = make_valid_order(
            ordered_on=date(2026, 1, 1),
            delivery_on=date(2026, 1, 2),
        )
        self.assertEqual(validate(order), [])

    def test_delivery_on_the_order_date_is_rejected(self):
        order = make_valid_order(
            ordered_on=date(2026, 1, 1),
            delivery_on=date(2026, 1, 1),
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_the_order_date_is_rejected(self):
        order = make_valid_order(
            ordered_on=date(2026, 1, 2),
            delivery_on=date(2026, 1, 1),
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])


class MultipleErrorsTest(unittest.TestCase):
    def test_every_invalid_field_is_reported_at_once(self):
        order = make_valid_order(
            customer_email="buyer.example.com",
            item_quantity=0,
            payment_method="cash",
        )
        # 오류 순서는 약속된 계약이 아니므로 순서 없이 비교한다.
        self.assertCountEqual(
            validate(order),
            ["invalid_email", "invalid_quantity", "invalid_payment_method"],
        )


if __name__ == "__main__":
    unittest.main()
