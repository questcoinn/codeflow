import unittest
from datetime import date

from src.order_validator import Order, validate


def make_order(**overrides):
    """유효한 주문을 만든다. 테스트가 보려는 필드만 overrides로 바꾼다."""
    fields = dict(
        order_id="ORD-1",
        customer_id="CUST-1",
        customer_email="buyer@example.com",
        shipping_name="홍길동",
        shipping_phone="010-1234-5678",
        shipping_address="서울시 중구 세종대로 110",
        shipping_zip="04524",
        item_sku="SKU-1",
        item_quantity=1,
        unit_price=1000,
        payment_method="card",
        ordered_on=date(2025, 1, 10),
        delivery_on=date(2025, 1, 11),
    )
    fields.update(overrides)
    return Order(**fields)


class ValidOrderTest(unittest.TestCase):
    def test_valid_order_has_no_errors(self):
        self.assertEqual(validate(make_order()), [])


class FieldRuleTestCase(unittest.TestCase):
    """한 필드의 값들을 표로 검사한다. 다른 에러가 섞이지 않는지도 함께 확인한다."""

    def assert_accepted(self, field, values):
        for value in values:
            with self.subTest(field=field, value=value):
                self.assertEqual(validate(make_order(**{field: value})), [])

    def assert_rejected(self, field, values, error):
        for value in values:
            with self.subTest(field=field, value=value):
                self.assertEqual(validate(make_order(**{field: value})), [error])


class EmailTest(FieldRuleTestCase):
    def test_email_with_at_sign_is_accepted(self):
        self.assert_accepted("customer_email", ["a@b.co"])

    def test_email_without_at_sign_is_rejected(self):
        self.assert_rejected(
            "customer_email", ["buyer.example.com", ""], "invalid_email"
        )


class ZipTest(FieldRuleTestCase):
    def test_five_digit_zip_is_accepted(self):
        self.assert_accepted("shipping_zip", ["00000", "99999"])

    def test_zip_with_wrong_length_is_rejected(self):
        self.assert_rejected("shipping_zip", ["", "1234", "123456"], "invalid_zip")

    def test_zip_with_non_digits_is_rejected(self):
        self.assert_rejected(
            "shipping_zip", ["1234a", "12 34", "12-34", "-1234"], "invalid_zip"
        )


class QuantityTest(FieldRuleTestCase):
    def test_quantity_within_range_is_accepted(self):
        self.assert_accepted("item_quantity", [1, 99])

    def test_quantity_out_of_range_is_rejected(self):
        self.assert_rejected("item_quantity", [-1, 0, 100], "invalid_quantity")


class PriceTest(FieldRuleTestCase):
    def test_zero_or_positive_price_is_accepted(self):
        self.assert_accepted("unit_price", [0, 1])

    def test_negative_price_is_rejected(self):
        self.assert_rejected("unit_price", [-1], "invalid_price")


class PaymentMethodTest(FieldRuleTestCase):
    def test_supported_payment_methods_are_accepted(self):
        self.assert_accepted("payment_method", ["card", "bank_transfer"])

    def test_unsupported_payment_method_is_rejected(self):
        self.assert_rejected(
            "payment_method", ["cash", "", "CARD"], "invalid_payment_method"
        )


class DeliveryDateTest(unittest.TestCase):
    ORDERED_ON = date(2025, 1, 10)

    def errors_for(self, delivery_on):
        return validate(
            make_order(ordered_on=self.ORDERED_ON, delivery_on=delivery_on)
        )

    def test_delivery_after_order_date_is_accepted(self):
        self.assertEqual(self.errors_for(date(2025, 1, 11)), [])

    def test_delivery_on_order_date_is_rejected(self):
        self.assertEqual(self.errors_for(self.ORDERED_ON), ["invalid_delivery_date"])

    def test_delivery_before_order_date_is_rejected(self):
        self.assertEqual(
            self.errors_for(date(2025, 1, 9)), ["invalid_delivery_date"]
        )


class MultipleErrorsTest(unittest.TestCase):
    def test_all_errors_are_reported_together(self):
        order = make_order(
            customer_email="no-at-sign",
            shipping_zip="abc",
            item_quantity=0,
            unit_price=-1,
            payment_method="cash",
            delivery_on=date(2025, 1, 10),
        )

        self.assertCountEqual(
            validate(order),
            [
                "invalid_email",
                "invalid_zip",
                "invalid_quantity",
                "invalid_price",
                "invalid_payment_method",
                "invalid_delivery_date",
            ],
        )


if __name__ == "__main__":
    unittest.main()
