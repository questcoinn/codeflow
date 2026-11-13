import unittest
from dataclasses import replace
from datetime import date

from src.order_validator import Order, validate


def valid_order(**overrides):
    """모든 검증을 통과하는 주문에서 테스트가 보려는 필드만 바꿔 돌려준다."""
    order = Order(
        order_id="ORD-1",
        customer_id="CUST-1",
        customer_email="buyer@example.com",
        shipping_name="홍길동",
        shipping_phone="010-1234-5678",
        shipping_address="서울시 중구 세종대로 110",
        shipping_zip="04524",
        item_sku="SKU-1",
        item_quantity=1,
        unit_price=10_000,
        payment_method="card",
        ordered_on=date(2026, 1, 10),
        delivery_on=date(2026, 1, 12),
    )
    return replace(order, **overrides)


class ValidOrderTest(unittest.TestCase):
    def test_valid_order_has_no_errors(self):
        self.assertEqual(validate(valid_order()), [])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_rejected(self):
        order = valid_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_with_4_digits_is_rejected(self):
        order = valid_order(shipping_zip="0452")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_zip_with_6_digits_is_rejected(self):
        order = valid_order(shipping_zip="045241")
        self.assertEqual(validate(order), ["invalid_zip"])

    def test_zip_with_non_digit_is_rejected(self):
        order = valid_order(shipping_zip="0452A")
        self.assertEqual(validate(order), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_0_is_rejected(self):
        order = valid_order(item_quantity=0)
        self.assertEqual(validate(order), ["invalid_quantity"])

    def test_quantity_100_is_rejected(self):
        order = valid_order(item_quantity=100)
        self.assertEqual(validate(order), ["invalid_quantity"])

    def test_quantity_99_is_accepted(self):
        order = valid_order(item_quantity=99)
        self.assertEqual(validate(order), [])


class PriceTest(unittest.TestCase):
    def test_negative_price_is_rejected(self):
        order = valid_order(unit_price=-1)
        self.assertEqual(validate(order), ["invalid_price"])

    def test_zero_price_is_accepted(self):
        order = valid_order(unit_price=0)
        self.assertEqual(validate(order), [])


class PaymentMethodTest(unittest.TestCase):
    def test_bank_transfer_is_accepted(self):
        order = valid_order(payment_method="bank_transfer")
        self.assertEqual(validate(order), [])

    def test_unsupported_payment_method_is_rejected(self):
        order = valid_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_on_order_day_is_rejected(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 10))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_order_day_is_rejected(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 9))
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_on_day_after_order_is_accepted(self):
        order = valid_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 11))
        self.assertEqual(validate(order), [])


class MultipleErrorsTest(unittest.TestCase):
    def test_all_errors_are_reported_together(self):
        order = valid_order(customer_email="no-at-sign", item_quantity=0, payment_method="cash")
        # 오류 순서는 계약이 아니므로 순서와 무관하게 비교한다
        self.assertCountEqual(
            validate(order),
            ["invalid_email", "invalid_quantity", "invalid_payment_method"],
        )


if __name__ == "__main__":
    unittest.main()
