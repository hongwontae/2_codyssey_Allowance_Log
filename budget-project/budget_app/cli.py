
import argparse
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

from budget_app.commands.csv_commands import handle_export
from budget_app.commands.csv_commands import handle_import
from budget_app.commands.summary_commands import handle_summary
from budget_app.commands.search_commands import handle_search
from budget_app.commands.list_commands import handle_list
from budget_app.commands.delete_commands import handle_delete
from budget_app.commands.update_commands import handle_update
from budget_app.commands.add_commands import handle_add
from budget_app.commands.management import (
    handle_category,
    handle_budget,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부"
    )

    # 데이터 저장 폴더 옵션
    parser.add_argument(
        "--data-dir",
        default="data",
        help="데이터 저장 폴더 경로 (기본값: data)"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # add 명령어
    subparsers.add_parser("add", help="거래 추가")

    # delete 명령어
    delete_parser = subparsers.add_parser(
        "delete",
        help="거래 삭제"
    )
    delete_parser.add_argument(
        "--id",
        required=True,
        help="삭제할 거래 ID"
    )

    # update 명령어
    update_parser = subparsers.add_parser(
        "update",
        help="거래 수정"
    )

    update_parser.add_argument(
        "--id",
        required=True,
        help="수정할 거래 ID"
    )
    update_parser.add_argument(
        "--date",
        dest="transaction_date",
        help="수정할 날짜 (YYYY-MM-DD)"
    )
    update_parser.add_argument(
        "--type",
        dest="transaction_type",
        choices=["income", "expense"],
        help="수정할 거래 타입"
    )
    update_parser.add_argument(
        "--category",
        help="수정할 카테고리"
    )
    update_parser.add_argument(
        "--amount",
        type=int,
        help="수정할 금액"
    )
    update_parser.add_argument(
        "--memo",
        help="수정할 메모"
    )
    update_parser.add_argument(
        "--tags",
        help="수정할 태그 (쉼표로 구분)"
    )


    # list 명령어
    list_parser = subparsers.add_parser(
        "list",
        help="거래 목록 조회"
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="출력할 거래 개수"
    )

    # search 명령어
    search_parser = subparsers.add_parser(
        "search",
        help="거래 검색"
    )

    search_parser.add_argument(
        "--from",
        dest="date_from",
        help="검색 시작 날짜 (YYYY-MM-DD)"
    )
    search_parser.add_argument(
        "--to",
        dest="date_to",
        help="검색 종료 날짜 (YYYY-MM-DD)"
    )
    search_parser.add_argument(
        "--category",
        help="검색할 카테고리"
    )
    search_parser.add_argument(
        "--type",
        dest="transaction_type",
        choices=["income", "expense"],
        help="거래 타입"
    )
    search_parser.add_argument(
        "--q",
        dest="keyword",
        help="메모 검색 키워드"
    )
    search_parser.add_argument(
        "--tag",
        help="검색할 태그"
    )

    # summary 명령어
    summary_parser = subparsers.add_parser(
        "summary",
        help="월별 요약"
    )
    summary_parser.add_argument(
        "--month",
        required=True,
        help="조회할 월 (YYYY-MM)"
    )
    summary_parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="출력할 지출 카테고리 개수"
    )    

    # export 명령어
    export_parser = subparsers.add_parser(
        "export",
        help="거래 내역 CSV 내보내기"
    )

    export_parser.add_argument(
        "--out",
        required=True,
        help="저장할 CSV 파일 경로"
    )

    export_group = export_parser.add_mutually_exclusive_group(
        required=True
    )

    export_group.add_argument(
        "--month",
        help="내보낼 월 (YYYY-MM)"
    )

    export_group.add_argument(
        "--from",
        dest="date_from",
        help="시작 날짜 (YYYY-MM-DD)"
    )

    export_parser.add_argument(
        "--to",
        dest="date_to",
        help="종료 날짜 (YYYY-MM-DD)"
    )

    # import 명령어
    import_parser = subparsers.add_parser(
        "import",
        help="CSV 거래 내역 가져오기",
    )

    import_parser.add_argument(
        "--from",
        dest="input_file",
        required=True,
        help="가져올 CSV 파일 경로",
    )    

    # category 명령어
    category_parser = subparsers.add_parser(
        "category",
        help="카테고리 관리"
    )

    category_commands = category_parser.add_subparsers(
        dest="category_command",
        required=True
    )

    category_commands.add_parser(
        "add",
        help="카테고리 추가"
    )

    category_commands.add_parser(
        "list",
        help="카테고리 목록 조회"
    )

    category_commands.add_parser(
        "remove",
        help="카테고리 삭제"
    )


    # budget 명령어
    budget_parser = subparsers.add_parser(
        "budget",
        help="월별 예산 관리",
    )

    budget_commands = budget_parser.add_subparsers(
        dest="budget_command",
        required=True,
    )

    budget_set_parser = budget_commands.add_parser(
        "set",
        help="월별 예산 설정",
    )

    budget_set_parser.add_argument(
        "--month",
        required=True,
        help="예산을 설정할 월 (YYYY-MM)",
    )

    budget_set_parser.add_argument(
        "--amount",
        required=True,
        type=int,
        help="월 예산 금액",
    )

    args = parser.parse_args()

    # 저장소 및 서비스 초기화
    data_dir = Path(args.data_dir)

    transaction_repository = TransactionRepository(
        data_dir / "transactions.jsonl"
    )

    category_repository = CategoryRepository(
        data_dir / "categories.jsonl"
    )

    transaction_service = TransactionService(
        transaction_repository,
        category_repository,
    )
    
    category_service = CategoryService(
        category_repository
    )

    budget_repository = BudgetRepository(
        data_dir / "budgets.jsonl"
    )

    budget_service = BudgetService(
        budget_repository
    )


    # budget 명령어 처리
    if args.command == "budget":
        return handle_budget(args, budget_service)

    # category 명령어 처리
    if args.command == "category":
        return handle_category(
            args,
            category_service,
            transaction_repository,
        )

    # add 명령어 처리
    if args.command == "add":
        return handle_add(
            args,
            transaction_service,
        )
    
    # update 명령어 처리
    if args.command == "update":
        return handle_update(
            args,
            transaction_service,
        )

    # delete 명령어 처리
    if args.command == "delete":
        return handle_delete(
            args,
            transaction_repository,
        )


    # search 명령어 처리
    if args.command == "search":
        return handle_search(
            args,
            transaction_service,
        )

    # summary 명령어 처리
    if args.command == "summary":
        return handle_summary(
            args,
            transaction_service,
            budget_service,
        )


    # list 명령어 처리
    if args.command == "list":
        return handle_list(
            args,
            transaction_repository,
        )

    # export 명령어 처리
    if args.command == "export":
        return handle_export(
            args,
            transaction_repository,
        )
        
    # import 명령어 처리
    if args.command == "import":
        return handle_import(
            args,
            transaction_service,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
