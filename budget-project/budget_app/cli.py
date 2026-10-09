
import argparse
from pathlib import Path

from budget_app.repository import (
    TransactionRepository,
    CategoryRepository,
)
from budget_app.services import (
    TransactionService,
    CategoryService,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부"
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


    args = parser.parse_args()

    # 저장소 및 서비스 초기화
    data_dir = Path("data")

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

    # category 명령어 처리
    if args.command == "category":
        try:
            if args.category_command == "add":
                name = input("카테고리명: ").strip()
                category_service.add_category(name)
                print(f"[저장 완료] category={name}")

            elif args.category_command == "list":
                categories = category_service.list_categories()

                if not categories:
                    print("등록된 카테고리가 없습니다.")
                else:
                    for name in categories:
                        print(f"- {name}")

            elif args.category_command == "remove":
                name = input("삭제할 카테고리명: ").strip()
                category_service.remove_category(
                    name,
                    transaction_repository,
                )
                print(f"[삭제 완료] category={name}")

            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

    # add 명령어 처리
    if args.command == "add":
        try:
            transaction_date = input(
                "날짜(YYYY-MM-DD): "
            ).strip()
            transaction_type = input(
                "타입(income/expense): "
            ).strip()
            category = input("카테고리: ").strip()
            amount = int(input("금액(양수): ").strip())
            memo = input("메모(선택): ").strip()
            raw_tags = input(
                "태그(쉼표로 구분): "
            ).strip()

            tags = [
                tag.strip()
                for tag in raw_tags.split(",")
                if tag.strip()
            ]

            transaction = transaction_service.add_transaction(
                transaction_type=transaction_type,
                transaction_date=transaction_date,
                amount=amount,
                category=category,
                memo=memo,
                tags=tags,
            )

            print(f"[저장 완료] id={transaction.id}")
            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1
    
    # update 명령어 처리
    if args.command == "update":
        try:
            tags = None

            if args.tags is not None:
                tags = [
                    tag.strip()
                    for tag in args.tags.split(",")
                    if tag.strip()
                ]

            transaction = transaction_service.update_transaction(
                transaction_id=args.id,
                transaction_date=args.transaction_date,
                transaction_type=args.transaction_type,
                category=args.category,
                amount=args.amount,
                memo=args.memo,
                tags=tags,
            )

            print(f"[수정 완료] id={transaction.id}")
            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1


    # delete 명령어 처리
    if args.command == "delete":
        try:
            deleted = transaction_repository.delete(args.id)

            if deleted:
                print(f"[삭제 완료] id={args.id}")
                return 0

            print(f"[오류] 해당 거래 ID가 없습니다: {args.id}")
            return 1

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1


    # search 명령어 처리
    if args.command == "search":
        try:
            transactions = transaction_service.search_transactions(
                date_from=args.date_from,
                date_to=args.date_to,
                category=args.category,
                transaction_type=args.transaction_type,
                keyword=args.keyword,
                tag=args.tag,
            )

            if not transactions:
                print("검색 결과가 없습니다.")
                return 0

            for transaction in transactions:
                print(
                    f"{transaction.id} | {transaction.date} | "
                    f"{transaction.type} | {transaction.category} | "
                    f"{transaction.amount} | {transaction.memo}"
                )

            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1


    # list 명령어 처리
    if args.command == "list":
        if args.limit <= 0:
            print("[오류] --limit은 1 이상의 정수여야 합니다.")
            return 1

        transactions = sorted(
            transaction_repository.iter_transactions(),
            key=lambda transaction: (
                transaction.date,
                transaction.id
            ),
            reverse=True,
        )

        count = 0

        for transaction in transactions[:args.limit]:
            print(
                f"{transaction.id} | {transaction.date} | "
                f"{transaction.type} | {transaction.category} | "
                f"{transaction.amount} | {transaction.memo}"
            )
            count += 1

        if count == 0:
            print("거래 내역이 없습니다.")

        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
