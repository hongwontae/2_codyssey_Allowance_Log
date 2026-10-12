import csv
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from budget_app.cli import main


class BudgetAppCLITests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.csv_path = self.data_dir / "import.csv"

        # 거래를 추가할 수 있도록 카테고리 등록
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "categories.jsonl").write_text(
            '{"name": "food"}\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, *args):
        output = StringIO()

        with patch(
            "sys.argv",
            [
                "budget_app",
                "--data-dir",
                str(self.data_dir),
                *args,
            ],
        ):
            with redirect_stdout(output):
                exit_code = main()

        return exit_code, output.getvalue()

    def write_csv(self, fieldnames, rows):
        with self.csv_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_import_csv_success(self):
        self.write_csv(
            [
                "date",
                "type",
                "category",
                "amount",
                "memo",
                "tags",
            ],
            [
                {
                    "date": "2026-10-10",
                    "type": "expense",
                    "category": "food",
                    "amount": "5000",
                    "memo": "점심",
                    "tags": "meal",
                }
            ],
        )

        exit_code, output = self.run_cli(
            "import",
            "--from",
            str(self.csv_path),
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("imported=1", output)
        self.assertIn("skipped=0", output)

    def test_import_invalid_header_is_rejected(self):
        self.write_csv(
            ["date", "type"],
            [
                {
                    "date": "2026-10-10",
                    "type": "expense",
                }
            ],
        )

        exit_code, output = self.run_cli(
            "import",
            "--from",
            str(self.csv_path),
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("CSV 헤더가 올바르지 않습니다", output)

    def test_import_invalid_transaction_is_skipped(self):
        self.write_csv(
            ["date", "type", "category", "amount"],
            [
                {
                    "date": "2026-10-10",
                    "type": "expense",
                    "category": "food",
                    "amount": "0",
                }
            ],
        )

        exit_code, output = self.run_cli(
            "import",
            "--from",
            str(self.csv_path),
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("imported=0", output)
        self.assertIn("skipped=1", output)

    def test_import_duplicate_is_skipped(self):
        self.write_csv(
            ["date", "type", "category", "amount", "memo", "tags"],
            [
                {
                    "date": "2026-10-10",
                    "type": "expense",
                    "category": "food",
                    "amount": "5000",
                    "memo": "점심",
                    "tags": "meal",
                }
            ],
        )

        first_code, _ = self.run_cli(
            "import", "--from", str(self.csv_path)
        )
        second_code, output = self.run_cli(
            "import", "--from", str(self.csv_path)
        )

        self.assertEqual(first_code, 0)
        self.assertEqual(second_code, 0)
        self.assertIn("imported=0", output)
        self.assertIn("skipped=1", output)
    def test_export_csv_by_month(self):
        # 1. 10월 거래 추가
        with patch(
            "builtins.input",
            side_effect=[
                "2026-10-10",
                "expense",
                "food",
                "5000",
                "점심",
                "meal",
            ],
        ):
            exit_code, _ = self.run_cli("add")

        self.assertEqual(exit_code, 0)

        # 2. 9월 거래 추가
        with patch(
            "builtins.input",
            side_effect=[
                "2026-09-10",
                "expense",
                "food",
                "3000",
                "간식",
                "snack",
            ],
        ):
            exit_code, _ = self.run_cli("add")

        self.assertEqual(exit_code, 0)

        # 3. 10월 거래만 CSV로 내보내기
        output_path = self.data_dir / "october.csv"

        exit_code, output = self.run_cli(
            "export",
            "--out",
            str(output_path),
            "--month",
            "2026-10",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("1 records", output)
        self.assertTrue(output_path.exists())

        # 4. CSV 내용을 확인
        with output_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-10-10")
        self.assertEqual(rows[0]["category"], "food")
        self.assertEqual(rows[0]["amount"], "5000")
        self.assertEqual(rows[0]["memo"], "점심")

    def test_search_by_category(self):
        # 테스트용 거래 추가
        with patch(
            "builtins.input",
            side_effect=[
                "2026-10-10",
                "expense",
                "food",
                "5000",
                "점심",
                "meal",
            ],
        ):
            self.run_cli("add")

        exit_code, output = self.run_cli(
            "search",
            "--category",
            "food",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("food", output)
        self.assertIn("점심", output)

    def test_search_by_date_range(self):
        with patch(
            "builtins.input",
            side_effect=[
                "2026-10-10",
                "expense",
                "food",
                "5000",
                "점심",
                "meal",
            ],
        ):
            self.run_cli("add")

        exit_code, output = self.run_cli(
            "search",
            "--from",
            "2026-10-01",
            "--to",
            "2026-10-31",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("2026-10-10", output)

    def test_search_by_keyword(self):
        with patch(
            "builtins.input",
            side_effect=[
                "2026-10-10",
                "expense",
                "food",
                "5000",
                "점심 식사",
                "meal",
            ],
        ):
            self.run_cli("add")

        exit_code, output = self.run_cli(
            "search",
            "--q",
            "점심",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("점심 식사", output)

    def test_search_by_tag(self):
        with patch(
            "builtins.input",
            side_effect=[
                "2026-10-10",
                "expense",
                "food",
                "5000",
                "점심",
                "meal",
            ],
        ):
            self.run_cli("add")

        exit_code, output = self.run_cli(
            "search",
            "--tag",
            "meal",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("점심", output)



if __name__ == "__main__":
    unittest.main()