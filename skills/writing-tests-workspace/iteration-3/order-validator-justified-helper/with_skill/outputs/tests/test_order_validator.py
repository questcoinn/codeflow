import unittest
from dataclasses import replace
from datetime import date

from src.order_validator import Order, validate


def valid_order(**overrides):
    """모든 검증을 통과하는 주문. 테스트에서 확인할 필드만 인자로 바꾼다."""
    order = Order(
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
        ordered_on=date(2026, 1, 10),
        delivery_on=date(2026, 1, 11),
    )
    return replace(order, **overrides)


class ValidOrderTest(unittest.TestCase):
    def test_valid_order_has_no_errors(self):
        self.assertEqual(validate(valid_order()), [])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_invalid(self):
        order = valid_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_with_4_digits_is_invalid(self):
        self.assertEqual(validate(valid_order(shipping_zip="1234")), ["invalid_zip"])

    def test_zip_with_6_digits_is_invalid(self):
        self.assertEqual(validate(valid_order(shipping_zip="123456")), ["invalid_zip"])

    def test_zip_with_non_digit_character_is_invalid(self):
        self.assertEqual(validate(valid_order(shipping_zip="1234A")), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_0_is_invalid(self):
        self.assertEqual(validate(valid_order(item_quantity=0)), ["invalid_quantity"])

    def test_quantity_1_is_allowed(self):
        self.assertEqual(validate(valid_order(item_quantity=1)), [])

    def test_quantity_99_is_allowed(self):
        self.assertEqual(validate(valid_order(item_quantity=99)), [])

    def test_quantity_100_is_invalid(self):
        self.assertEqual(validate(valid_order(item_quantity=100)), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_price_0_is_allowed(self):
        self.assertEqual(validate(valid_order(unit_price=0)), [])

    def test_negative_price_is_invalid(self):
        self.assertEqual(validate(valid_order(unit_price=-1)), ["invalid_price"])


class PaymentMethodTest(unittest.TestCase):
    def test_bank_transfer_is_allowed(self):
        self.assertEqual(validate(valid_order(payment_method="bank_transfer")), [])

    def test_unknown_payment_method_is_invalid(self):
        order = valid_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_on_order_date_is_invalid(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 10))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_order_date_is_invalid(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 9))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_day_after_order_date_is_allowed(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 11))
        self.assertEqual(validate(order), [])


class MultipleErrorsTest(unittest.TestCase):
    def test_all_violations_are_reported_together(self):
        order = valid_order(customer_email="no-at-sign", item_quantity=0, unit_price=-1)
        # 결과 순서는 계약이 아니므로 집합으로 비교한다
        self.assertEqual(
            set(validate(order)),
            {"invalid_email", "invalid_quantity", "invalid_price"},
        )


if __name__ == "__main__":
    unittest.main()
