import tempfile
import unittest
from pathlib import Path

from budget_app.repository import (
    TransactionRepository,
)

from budget_app.models import Transaction

class TransactionRepositoryTests(unittest.TestCase):
    def setUp(self):
        # 각 테스트마다 별도의 임시 디렉터리 생성
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

        self.file_path = self.data_dir / "transactions.jsonl"
        self.repository = TransactionRepository(self.file_path)

    def tearDown(self):
        # 테스트가 끝나면 임시 디렉터리 정리
        self.temp_dir.cleanup()

    def test_repository_creates_file_if_missing(self):
        # 저장 파일이 없다면 저장소 초기화 후 파일이 생성되는지 확인
        self.assertTrue(self.file_path.exists())

    def test_empty_repository_returns_no_transactions(self):
        # 빈 저장소를 조회했을 때 거래가 없는지 확인
        transactions = list(self.repository.iter_transactions())

        self.assertEqual(transactions, [])
   
    def test_add_transaction(self):
        transaction = Transaction(
            id="TX-000001",
            type="expense",
            date="2026-10-12",
            amount=5000,
            category="food",
            memo="점심",
            tags=["meal"],
        )

        self.repository.add(transaction)

        saved = list(self.repository.iter_transactions())

        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].id, "TX-000001")
        self.assertEqual(saved[0].amount, 5000)
        self.assertEqual(saved[0].memo, "점심")
        self.assertEqual(saved[0].tags, ["meal"])

    def test_delete_transaction(self):
        transaction = Transaction(
            id="TX-000001",
            type="expense",
            date="2026-10-12",
            amount=5000,
            category="food",
        )
        self.repository.add(transaction)

        result = self.repository.delete("TX-000001")

        self.assertTrue(result)
        self.assertEqual(
            list(self.repository.iter_transactions()),
            [],
        )

    def test_delete_nonexistent_transaction(self):
        result = self.repository.delete("TX-999999")

        self.assertFalse(result)

    def test_update_transaction(self):
        transaction = Transaction(
            id="TX-000001",
            type="expense",
            date="2026-10-12",
            amount=5000,
            category="food",
            memo="점심",
            tags=["meal"],
        )
        self.repository.add(transaction)

        updated = Transaction(
            id="TX-000001",
            type="expense",
            date="2026-10-12",
            amount=7000,
            category="food",
            memo="저녁 식사",
            tags=["meal"],
        )

        result = self.repository.update(updated)

        self.assertTrue(result)

        saved = list(self.repository.iter_transactions())
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].amount, 7000)
        self.assertEqual(saved[0].memo, "저녁 식사")

    def test_update_nonexistent_transaction(self):
        transaction = Transaction(
            id="TX-999999",
            type="expense",
            date="2026-10-12",
            amount=7000,
            category="food",
            memo="저녁 식사",
            tags=["meal"],
        )

        result = self.repository.update(transaction)

        self.assertFalse(result)
        self.assertEqual(
            list(self.repository.iter_transactions()),
            [],
        )
    def test_invalid_json_line_raises_error(self):
        # 잘못된 JSON 데이터 작성
        self.repository.file_path.write_text(
            '{"id": "TX-000001"}\n'
            '{broken json}\n',
            encoding="utf-8",
        )

        # 잘못된 데이터가 있으면 오류가 발생해야 함
        with self.assertRaises(ValueError):
            list(self.repository.iter_transactions())


if __name__ == "__main__":
    unittest.main()
