
import json
from pathlib import Path
from collections.abc import Iterator

from budget_app.models import Transaction


class TransactionRepository:
    def __init__(self, file_path: Path):
        self.file_path = file_path

        # 저장 폴더가 없으면 생성
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # 저장 파일이 없으면 생성
        self.file_path.touch(exist_ok=True)

    def iter_transactions(self) -> Iterator[Transaction]:
        """거래 내역을 한 건씩 읽어 반환한다."""
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                # 빈 줄은 건너뛴다.
                if not line.strip():
                    continue

                # JSON 문자열 -> Python 딕셔너리
                data = json.loads(line)

                # 딕셔너리 -> Transaction 객체
                yield Transaction(**data)
    
    def add(self, transaction: Transaction) -> None:
        """거래 한 건을 JSONL 파일에 추가한다."""
        data = {
            "id": transaction.id,
            "type": transaction.type,
            "date": transaction.date,
            "amount": transaction.amount,
            "category": transaction.category,
            "memo": transaction.memo,
            "tags": transaction.tags or [],
        }

        # 기존 파일의 마지막 줄이 줄바꿈으로 끝나는지 확인
        with self.file_path.open("rb+") as file:
            file.seek(0, 2)
            file_size = file.tell()

            if file_size > 0:
                file.seek(-1, 2)
                last_byte = file.read(1)

                if last_byte != b"\n":
                    file.write(b"\n")

            file.write(
                (
                    json.dumps(data, ensure_ascii=False) + "\n"
                ).encode("utf-8")
            )
            
    def delete(self, transaction_id: str) -> bool:
        """ID에 해당하는 거래를 삭제한다."""
        temp_path = self.file_path.with_suffix(".tmp")
        found = False

        with self.file_path.open("r", encoding="utf-8") as source:
            with temp_path.open("w", encoding="utf-8") as target:
                for line in source:
                    if not line.strip():
                        continue

                    data = json.loads(line)

                    if data["id"] == transaction_id:
                        found = True
                        continue

                    target.write(
                        json.dumps(data, ensure_ascii=False) + "\n"
                    )

        if not found:
            temp_path.unlink(missing_ok=True)
            return False

        temp_path.replace(self.file_path)
        return True

    def update(self, transaction: Transaction) -> bool:
        """기존 거래를 수정한다. 대상 ID가 없으면 False를 반환한다."""
        temp_path = self.file_path.with_suffix(".tmp")
        found = False

        with self.file_path.open("r", encoding="utf-8") as source:
            with temp_path.open("w", encoding="utf-8") as target:
                for line in source:
                    if not line.strip():
                        continue

                    data = json.loads(line)

                    if data["id"] == transaction.id:
                        data = {
                            "id": transaction.id,
                            "type": transaction.type,
                            "date": transaction.date,
                            "amount": transaction.amount,
                            "category": transaction.category,
                            "memo": transaction.memo,
                            "tags": transaction.tags or [],
                        }
                        found = True

                    target.write(
                        json.dumps(data, ensure_ascii=False) + "\n"
                    )

        if not found:
            temp_path.unlink(missing_ok=True)
            return False

        temp_path.replace(self.file_path)
        return True

class CategoryRepository:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def iter_categories(self) -> Iterator[str]:
        """등록된 카테고리를 한 개씩 반환한다."""
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                data = json.loads(line)
                yield data["name"]

    def add(self, name: str) -> None:
        """카테고리를 파일에 추가한다."""
        data = {"name": name}

        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    def remove(self, name: str) -> bool:
        """카테고리를 삭제한다. 존재하지 않으면 False를 반환한다."""
        categories = list(self.iter_categories())

        if name not in categories:
            return False

        remaining = [category for category in categories if category != name]

        temp_path = self.file_path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            for category in remaining:
                data = {"name": category}
                file.write(json.dumps(data, ensure_ascii=False) + "\n")

        temp_path.replace(self.file_path)
        return True



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

