from datetime import date

from budget_app.repository import BudgetRepository

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