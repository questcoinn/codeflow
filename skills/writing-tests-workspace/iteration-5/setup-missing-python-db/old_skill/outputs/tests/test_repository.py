import sqlite3
import unittest

from inventory.repository import StockRepository
from inventory.stock import Stock, reserve


class StockRepositoryTest(unittest.TestCase):
    def setUp(self):
        # 실제 SQLite를 메모리 모드로 쓴다. 테스트마다 새 DB라 서로 영향이 없다.
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)

    def test_get_returns_none_for_unknown_sku(self):
        repo = StockRepository(self.conn)

        self.assertIsNone(repo.get("UNKNOWN"))

    def test_saved_stock_can_be_read_back(self):
        repo = StockRepository(self.conn)

        repo.save(Stock("APPLE", on_hand=10, reserved=3))

        self.assertEqual(repo.get("APPLE"), Stock("APPLE", on_hand=10, reserved=3))

    def test_saving_a_reservation_overwrites_the_existing_row(self):
        repo = StockRepository(self.conn)
        repo.save(Stock("APPLE", on_hand=10, reserved=0))

        repo.save(reserve(repo.get("APPLE"), 4))

        self.assertEqual(repo.get("APPLE"), Stock("APPLE", on_hand=10, reserved=4))


if __name__ == "__main__":
    unittest.main()
