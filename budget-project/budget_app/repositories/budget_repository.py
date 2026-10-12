from collections.abc import Iterator
import json
from pathlib import Path


class BudgetRepository:
    """월별 예산을 JSONL 파일에 저장하고 조회한다."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

        # 저장 폴더가 없으면 생성
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # 파일이 없으면 생성
        self.file_path.touch(exist_ok=True)

    def iter_budgets(self) -> Iterator[dict]:
        """저장된 예산을 한 건씩 읽는다."""
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                yield json.loads(line)

    def get_amount(self, month: str) -> int | None:
        """특정 월의 예산을 조회한다."""
        for budget in self.iter_budgets():
            if budget["month"] == month:
                return budget["amount"]

        return None

    def set_budget(self, month: str, amount: int) -> None:
        """특정 월의 예산을 저장하거나 갱신한다."""
        if amount <= 0:
            raise ValueError("예산은 1원 이상이어야 합니다.")

        budgets = [
            budget
            for budget in self.iter_budgets()
            if budget["month"] != month
        ]

        budgets.append({
            "month": month,
            "amount": amount,
        })

        # 임시 파일에 먼저 작성
        temp_path = self.file_path.with_suffix(".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                for budget in budgets:
                    file.write(
                        json.dumps(budget, ensure_ascii=False) + "\n"
                    )

            # 작성이 끝난 파일로 교체
            temp_path.replace(self.file_path)

        finally:
            # 실패 시 남은 임시 파일 정리
            temp_path.unlink(missing_ok=True)

