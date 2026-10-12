from budget_app.repository import CategoryRepository
from budget_app.repository import TransactionRepository

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
