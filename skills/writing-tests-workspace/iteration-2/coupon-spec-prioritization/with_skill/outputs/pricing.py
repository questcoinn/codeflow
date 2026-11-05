import logging

logger = logging.getLogger(__name__)

CURRENCY = "KRW"
MIN_ORDER_FOR_COUPON = 10_000


def apply_coupons(subtotal, coupons):
    """coupons: [{"type": "percent"|"fixed", "value": int, "stackable": bool}]"""
    if subtotal < MIN_ORDER_FOR_COUPON:
        return subtotal
    if len(coupons) > 1 and not all(c["stackable"] for c in coupons):
        raise ValueError("non-stackable coupon cannot be combined")

    discount = 0
    for coupon in coupons:
        if coupon["type"] == "percent":
            discount += subtotal * coupon["value"] // 100
        else:
            discount += coupon["value"]

    total = max(subtotal - discount, 0)
    logger.info("coupon applied: subtotal=%s total=%s", subtotal, total)
    return total
