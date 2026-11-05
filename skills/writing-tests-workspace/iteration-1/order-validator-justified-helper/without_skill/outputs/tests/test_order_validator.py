import unittest
from datetime import date

from src.order_validator import Order, validate


def make_order(**overrides):
    """Return a valid Order; pass only the fields the test cares about."""
    fields = dict(
        order_id="ORD-1",
        customer_id="CUST-1",
        customer_email="buyer@example.com",
        shipping_name="Hong Gildong",
        shipping_phone="010-1234-5678",
        shipping_address="1 Sejong-daero, Seoul",
        shipping_zip="04524",
        item_sku="SKU-1",
        item_quantity=1,
        unit_price=1000,
        payment_method="card",
        ordered_on=date(2026, 1, 10),
        delivery_on=date(2026, 1, 11),
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

    def test_empty_email_is_invalid(self):
        self.assertEqual(validate(make_order(customer_email="")), ["invalid_email"])


class ZipTest(unittest.TestCase):
    def test_zip_must_be_exactly_five_digits(self):
        for bad_zip in ("", "1234", "123456", "1234a", "12 34", "12-34"):
            with self.subTest(shipping_zip=bad_zip):
                order = make_order(shipping_zip=bad_zip)
                self.assertEqual(validate(order), ["invalid_zip"])

    def test_zip_with_leading_zero_is_valid(self):
        self.assertEqual(validate(make_order(shipping_zip="00501")), [])


class QuantityTest(unittest.TestCase):
    def test_quantity_inside_range_is_valid(self):
        for quantity in (1, 99):
            with self.subTest(item_quantity=quantity):
                self.assertEqual(validate(make_order(item_quantity=quantity)), [])

    def test_quantity_outside_range_is_invalid(self):
        for quantity in (-1, 0, 100):
            with self.subTest(item_quantity=quantity):
                order = make_order(item_quantity=quantity)
                self.assertEqual(validate(order), ["invalid_quantity"])


class PriceTest(unittest.TestCase):
    def test_zero_price_is_valid(self):
        self.assertEqual(validate(make_order(unit_price=0)), [])

    def test_negative_price_is_invalid(self):
        self.assertEqual(validate(make_order(unit_price=-1)), ["invalid_price"])


class PaymentMethodTest(unittest.TestCase):
    def test_supported_payment_methods_are_valid(self):
        for method in ("card", "bank_transfer"):
            with self.subTest(payment_method=method):
                self.assertEqual(validate(make_order(payment_method=method)), [])

    def test_unsupported_payment_method_is_invalid(self):
        for method in ("", "cash", "CARD"):
            with self.subTest(payment_method=method):
                order = make_order(payment_method=method)
                self.assertEqual(validate(order), ["invalid_payment_method"])


class DeliveryDateTest(unittest.TestCase):
    def test_delivery_the_day_after_ordering_is_valid(self):
        order = make_order(ordered_on=date(2026, 1, 10), delivery_on=date(2026, 1, 11))
        self.assertEqual(validate(order), [])

    def test_delivery_on_or_before_order_date_is_invalid(self):
        for delivery_on in (date(2026, 1, 10), date(2026, 1, 9)):
            with self.subTest(delivery_on=delivery_on):
                order = make_order(ordered_on=date(2026, 1, 10), delivery_on=delivery_on)
                self.assertEqual(validate(order), ["invalid_delivery_date"])


class MultipleErrorsTest(unittest.TestCase):
    def test_all_errors_are_reported_in_check_order(self):
        order = make_order(
            customer_email="no-at-sign",
            shipping_zip="1",
            item_quantity=0,
            unit_price=-1,
            payment_method="cash",
            delivery_on=date(2026, 1, 10),
        )
        self.assertEqual(
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
