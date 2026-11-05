import unittest
from datetime import date

from src.order_validator import Order, validate


def make_order(**overrides):
    """유효한 주문을 만든다. 테스트에서 중요한 필드는 인자로 넘겨 드러낸다."""
    fields = dict(
        order_id="ORD-1",
        customer_id="CUST-1",
        customer_email="buyer@example.com",
        shipping_name="김철수",
        shipping_phone="010-1234-5678",
        shipping_address="서울시 강남구 테헤란로 1",
        shipping_zip="06236",
        item_sku="SKU-1",
        item_quantity=1,
        unit_price=10_000,
        payment_method="card",
        ordered_on=date(2026, 1, 10),
        delivery_on=date(2026, 1, 13),
    )
    fields.update(overrides)
    return Order(**fields)


class ValidOrderTest(unittest.TestCase):
    def test_valid_order_has_no_errors(self):
        self.assertEqual(validate(make_order()), [])


class EmailTest(unittest.TestCase):
    def test_email_without_at_sign_is_invalid(self):
        order = make_order(customer_email="buyer.example.com")
        self.assertEqual(validate(order), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_with_leading_zero_is_valid(self):
        order = make_order(shipping_zip="01234")
        self.assertEqual(validate(order), [])

    def test_zip_that_is_not_exactly_five_digits_is_invalid(self):
        for shipping_zip in ["", "1234", "123456", "1234a", "12-34"]:
            with self.subTest(shipping_zip=shipping_zip):
                order = make_order(shipping_zip=shipping_zip)
                self.assertEqual(validate(order), ["invalid_zip"])


class QuantityTest(unittest.TestCase):
    def test_quantity_from_1_to_99_is_valid(self):
        for item_quantity in [1, 99]:
            with self.subTest(item_quantity=item_quantity):
                order = make_order(item_quantity=item_quantity)
                self.assertEqual(validate(order), [])

    def test_quantity_outside_1_to_99_is_invalid(self):
        for item_quantity in [-1, 0, 100]:
            with self.subTest(item_quantity=item_quantity):
                order = make_order(item_quantity=item_quantity)
                self.assertEqual(validate(order), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_zero_price_is_valid(self):
        order = make_order(unit_price=0)
        self.assertEqual(validate(order), [])

    def test_negative_price_is_invalid(self):
        order = make_order(unit_price=-1)
        self.assertEqual(validate(order), ["invalid_price"])


class PaymentMethodTest(unittest.TestCase):
    def test_card_and_bank_transfer_are_valid(self):
        for payment_method in ["card", "bank_transfer"]:
            with self.subTest(payment_method=payment_method):
                order = make_order(payment_method=payment_method)
                self.assertEqual(validate(order), [])

    def test_other_payment_method_is_invalid(self):
        order = make_order(payment_method="cash")
        self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_the_day_after_order_is_valid(self):
        order = make_order(
            ordered_on=date(2026, 1, 10),
            delivery_on=date(2026, 1, 11),
        )
        self.assertEqual(validate(order), [])

    def test_delivery_on_the_order_date_is_invalid(self):
        order = make_order(
            ordered_on=date(2026, 1, 10),
            delivery_on=date(2026, 1, 10),
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])

    def test_delivery_before_the_order_date_is_invalid(self):
        order = make_order(
            ordered_on=date(2026, 1, 10),
            delivery_on=date(2026, 1, 9),
        )
        self.assertEqual(validate(order), ["invalid_delivery_date"])


class MultipleErrorsTest(unittest.TestCase):
    def test_every_invalid_field_is_reported_at_once(self):
        order = make_order(
            customer_email="no-at-sign",
            shipping_zip="1234",
            item_quantity=0,
            unit_price=-1,
            payment_method="cash",
            ordered_on=date(2026, 1, 10),
            delivery_on=date(2026, 1, 10),
        )
        # 오류 순서를 약속한 곳이 없어 순서는 고정하지 않는다.
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
