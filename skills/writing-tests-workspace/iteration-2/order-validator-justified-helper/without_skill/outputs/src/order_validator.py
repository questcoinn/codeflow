from dataclasses import dataclass
from datetime import date


@dataclass
class Order:
    order_id: str
    customer_id: str
    customer_email: str
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_zip: str
    item_sku: str
    item_quantity: int
    unit_price: int
    payment_method: str
    ordered_on: date
    delivery_on: date


def validate(order):
    errors = []
    if "@" not in order.customer_email:
        errors.append("invalid_email")
    if len(order.shipping_zip) != 5 or not order.shipping_zip.isdigit():
        errors.append("invalid_zip")
    if order.item_quantity < 1 or order.item_quantity > 99:
        errors.append("invalid_quantity")
    if order.unit_price < 0:
        errors.append("invalid_price")
    if order.payment_method not in ("card", "bank_transfer"):
        errors.append("invalid_payment_method")
    if order.delivery_on <= order.ordered_on:
        errors.append("invalid_delivery_date")
    return errors
