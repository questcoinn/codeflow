import sqlite3

from inventory.stock import Stock


class StockRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        conn.execute(
            "CREATE TABLE IF NOT EXISTS stock ("
            "sku TEXT PRIMARY KEY, on_hand INTEGER NOT NULL, reserved INTEGER NOT NULL)"
        )

    def get(self, sku: str) -> Stock | None:
        row = self.conn.execute(
            "SELECT sku, on_hand, reserved FROM stock WHERE sku = ?", (sku,)
        ).fetchone()
        return Stock(*row) if row else None

    def save(self, stock: Stock) -> None:
        self.conn.execute(
            "INSERT INTO stock (sku, on_hand, reserved) VALUES (?, ?, ?) "
            "ON CONFLICT(sku) DO UPDATE SET on_hand = excluded.on_hand, reserved = excluded.reserved",
            (stock.sku, stock.on_hand, stock.reserved),
        )
        self.conn.commit()
