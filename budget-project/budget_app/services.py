
from datetime import date
from pathlib import Path

from budget_app.models import Transaction
from budget_app.repository import TransactionRepository
from budget_app.repository import CategoryRepository
from budget_app.repository import BudgetRepository

from budget_app.decorators import measure_time


class TransactionService:
    def __init__(self, repository: TransactionRepository, category_repository: CategoryRepository):
        self.repository = repository
        self.category_repository = category_repository
        
    def update_transaction(
        self,
        transaction_id: str,
        transaction_date: str | None = None,
        transaction_type: str | None = None,
        category: str | None = None,
        amount: int | None = None,
        memo: str | None = None,
        tags: list[str] | None = None,
    ) -> Transaction:
        """기존 거래의 지정된 필드만 수정한다."""

        # 수정 대상 거래 찾기
        transaction = next(
            (
                item
                for item in self.repository.iter_transactions()
                if item.id == transaction_id
            ),
            None,
        )

        if transaction is None:
            raise ValueError(
                f"존재하지 않는 거래 ID입니다: {transaction_id}"
            )

        # 입력받은 값만 기존 값에 반영
        new_date = (
            transaction_date
            if transaction_date is not None
            else transaction.date
        )
        new_type = (
            transaction_type
            if transaction_type is not None
            else transaction.type
        )
        new_category = (
            category
            if category is not None
            else transaction.category
        )
        new_amount = (
            amount
            if amount is not None
            else transaction.amount
        )
        new_memo = (
            memo if memo is not None else transaction.memo
        )
        new_tags = (
            tags if tags is not None else transaction.tags
        )

        # 날짜 검증
        try:
            date.fromisoformat(new_date)
        except ValueError:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. 예: 2026-10-09"
            ) from None

        # 타입 검증
        if new_type not in ("income", "expense"):
            raise ValueError(
                "타입은 income 또는 expense여야 합니다."
            )

        # 금액 검증
        if new_amount <= 0:
            raise ValueError("금액은 1 이상의 정수여야 합니다.")

        # 카테고리 검증
        categories = set(
            self.category_repository.iter_categories()
        )
        if new_category not in categories:
            raise ValueError(
                f"등록되지 않은 카테고리입니다: {new_category}"
            )

        # 수정된 거래 객체 생성
        updated_transaction = Transaction(
            id=transaction.id,
            type=new_type,
            date=new_date,
            amount=new_amount,
            category=new_category,
            memo=new_memo,
            tags=new_tags,
        )

        # 저장소에 수정 요청
        if not self.repository.update(updated_transaction):
            raise ValueError(
                f"거래 수정에 실패했습니다: {transaction_id}"
            )

        return updated_transaction

    def add_transaction(
        self,
        transaction_type: str,
        transaction_date: str,
        amount: int,
        category: str,
        memo: str = "",
        tags: list[str] | None = None,
    ) -> Transaction:
        # 거래 타입 검증
        if transaction_type not in ("income", "expense"):
            raise ValueError("타입은 income 또는 expense여야 합니다.")

        categories = set(self.category_repository.iter_categories())

        if category not in categories:
            raise ValueError(
                f"등록되지 않은 카테고리입니다: {category}. "
                "category add로 먼저 등록하세요."
            )
        
        # 날짜 검증
        try:
            date.fromisoformat(transaction_date)
        except ValueError:
            raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from None

        # 금액 검증
        if amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")

        # 거래 ID 생성
        existing_ids = [
            transaction.id
            for transaction in self.repository.iter_transactions()
        ]

        next_id = len(existing_ids) + 1
        transaction_id = f"TX-{next_id:06d}"

        while transaction_id in existing_ids:
            next_id += 1
            transaction_id = f"TX-{next_id:06d}"

        transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            date=transaction_date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags or [],
        )

        self.repository.add(transaction)
        return transaction

    def search_transactions(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
        keyword: str | None = None,
        tag: str | None = None,
    ) -> list[Transaction]:
        """조건에 맞는 거래를 검색해 최신순으로 반환한다."""

        # 검색 날짜 검증
        for value in (date_from, date_to):
            if value is not None:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    raise ValueError(
                        "날짜는 YYYY-MM-DD 형식이어야 합니다."
                    ) from None

        if date_from and date_to and date_from > date_to:
            raise ValueError(
                "시작 날짜는 종료 날짜보다 늦을 수 없습니다."
            )

        if transaction_type is not None:
            if transaction_type not in ("income", "expense"):
                raise ValueError(
                    "타입은 income 또는 expense여야 합니다."
                )

        results = []

        for transaction in self.repository.iter_transactions():
            if date_from and transaction.date < date_from:
                continue

            if date_to and transaction.date > date_to:
                continue

            if category and transaction.category != category:
                continue

            if (
                transaction_type
                and transaction.type != transaction_type
            ):
                continue

            if keyword and keyword.casefold() not in transaction.memo.casefold():
                continue

            if tag and tag not in (transaction.tags or []):
                continue

            results.append(transaction)

        results.sort(
            key=lambda item: (item.date, item.id),
            reverse=True,
        )

        return results

    @measure_time
    def summary_month(
        self,
        month: str,
        top: int = 3,
    ) -> dict:
        """월별 수입, 지출, 잔액과 카테고리별 지출을 계산한다."""

        # 월 형식 검증
        try:
            parsed_month = date.fromisoformat(month + "-01")
        except ValueError:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            ) from None

        if parsed_month.strftime("%Y-%m") != month:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            )

        if top <= 0:
            raise ValueError("top은 1 이상의 정수여야 합니다.")

        total_income = 0
        total_expense = 0
        category_expenses: dict[str, int] = {}
        count = 0

        for transaction in self.repository.iter_transactions():
            if transaction.date[:7] != month:
                continue

            count += 1

            if transaction.type == "income":
                total_income += transaction.amount
            else:
                total_expense += transaction.amount
                category_expenses[transaction.category] = (
                    category_expenses.get(transaction.category, 0)
                    + transaction.amount
                )

        top_categories = sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:top]

        return {
            "month": month,
            "count": count,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "top_categories": top_categories,
        }

class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def add_category(self, name: str) -> None:
        name = name.strip()

        if not name:
            raise ValueError("카테고리 이름을 입력해야 합니다.")

        categories = set(self.repository.iter_categories())

        if name in categories:
            raise ValueError(f"이미 등록된 카테고리입니다: {name}")

        self.repository.add(name)

    def list_categories(self) -> list[str]:
        return sorted(self.repository.iter_categories())

    def remove_category(
        self,
        name: str,
        transaction_repository: TransactionRepository,
    ) -> None:
        name = name.strip()

        if not name:
            raise ValueError("카테고리 이름을 입력해야 합니다.")

        for transaction in transaction_repository.iter_transactions():
            if transaction.category == name:
                raise ValueError(
                    f"'{name}' 카테고리를 사용하는 거래가 있어 삭제할 수 없습니다."
                )

        if not self.repository.remove(name):
            raise ValueError(f"존재하지 않는 카테고리입니다: {name}")

class BudgetService:
    def __init__(self, repository: BudgetRepository):
        self.repository = repository

    def set_budget(self, month: str, amount: int) -> None:
        """월별 예산을 검증하고 저장한다."""

        # 월 형식 검증
        try:
            parsed_month = date.fromisoformat(month + "-01")
        except ValueError:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            ) from None

        if parsed_month.strftime("%Y-%m") != month:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            )

        if amount <= 0:
            raise ValueError("예산은 1원 이상이어야 합니다.")

        self.repository.set_budget(month, amount)

    def get_budget(self, month: str) -> int | None:
        """특정 월의 예산을 조회한다."""

        try:
            parsed_month = date.fromisoformat(month + "-01")
        except ValueError:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            ) from None

        if parsed_month.strftime("%Y-%m") != month:
            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
            )

        return self.repository.get_amount(month)