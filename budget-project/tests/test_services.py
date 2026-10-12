
import tempfile
import unittest
from pathlib import Path

from budget_app.repository import (
    TransactionRepository,
    CategoryRepository,
    BudgetRepository,
)
from budget_app.services import (
    TransactionService,
    CategoryService,
    BudgetService,
)


class BudgetAppServiceTests(unittest.TestCase):
    def setUp(self):
        # 테스트마다 독립적인 임시 디렉터리 사용
        self.temp_dir = tempfile.TemporaryDirectory()
        data_dir = Path(self.temp_dir.name)

        self.transaction_repository = TransactionRepository(
            data_dir / "transactions.jsonl"
        )
        self.category_repository = CategoryRepository(
            data_dir / "categories.jsonl"
        )
        self.budget_repository = BudgetRepository(
            data_dir / "budgets.jsonl"
        )

        self.transaction_service = TransactionService(
            self.transaction_repository,
            self.category_repository,
        )
        self.category_service = CategoryService(
            self.category_repository
        )
        self.budget_service = BudgetService(
            self.budget_repository
        )

        self.category_service.add_category("food")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_transaction(self):
        transaction = self.transaction_service.add_transaction(
            transaction_type="expense",
            transaction_date="2026-10-10",
            amount=5000,
            category="food",
            memo="점심",
            tags=["meal"],
        )

        self.assertEqual(transaction.id, "TX-000001")
        self.assertEqual(transaction.amount, 5000)

        saved = list(
            self.transaction_repository.iter_transactions()
        )
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].memo, "점심")

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.transaction_service.add_transaction(
                transaction_type="expense",
                transaction_date="2026-13-40",
                amount=5000,
                category="food",
            )

    def test_zero_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            self.transaction_service.add_transaction(
                transaction_type="expense",
                transaction_date="2026-10-10",
                amount=0,
                category="food",
            )

    def test_unregistered_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.transaction_service.add_transaction(
                transaction_type="expense",
                transaction_date="2026-10-10",
                amount=5000,
                category="unknown",
            )

    def test_monthly_summary(self):
        self.transaction_service.add_transaction(
            transaction_type="income",
            transaction_date="2026-10-01",
            amount=100000,
            category="food",
        )
        self.transaction_service.add_transaction(
            transaction_type="expense",
            transaction_date="2026-10-10",
            amount=5000,
            category="food",
        )

        result = self.transaction_service.summary_month(
            month="2026-10",
            top=3,
        )

        self.assertEqual(result["total_income"], 100000)
        self.assertEqual(result["total_expense"], 5000)
        self.assertEqual(result["balance"], 95000)
        self.assertEqual(result["count"], 2)

    def test_budget_is_persisted(self):
        self.budget_service.set_budget(
            month="2026-10",
            amount=500000,
        )

        self.assertEqual(
            self.budget_service.get_budget("2026-10"),
            500000,
        )

    def test_used_category_cannot_be_removed(self):
        self.transaction_service.add_transaction(
            transaction_type="expense",
            transaction_date="2026-10-10",
            amount=5000,
            category="food",
        )

        with self.assertRaises(ValueError):
            self.category_service.remove_category(
                "food",
                self.transaction_repository,
            )


if __name__ == "__main__":
    unittest.main()
