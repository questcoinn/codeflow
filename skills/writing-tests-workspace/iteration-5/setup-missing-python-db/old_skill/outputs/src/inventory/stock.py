from dataclasses import dataclass


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class Stock:
    sku: str
    on_hand: int
    reserved: int = 0

    @property
    def available(self) -> int:
        return self.on_hand - self.reserved


def reserve(stock: Stock, quantity: int) -> Stock:
    """주문 수량만큼 재고를 예약한다. 가용 재고보다 많으면 예약하지 않는다."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if quantity > stock.available:
        raise OutOfStock(stock.sku)
    return Stock(stock.sku, stock.on_hand, stock.reserved + quantity)


def release(stock: Stock, quantity: int) -> Stock:
    """주문 취소 시 예약을 풀어 준다. 예약된 수량보다 많이 풀 수는 없다."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    return Stock(stock.sku, stock.on_hand, max(0, stock.reserved - quantity))
