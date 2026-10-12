
import argparse
from pathlib import Path
import heapq


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

import csv
from datetime import date

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
        try:
            if args.budget_command == "set":
                budget_service.set_budget(
                    month=args.month,
                    amount=args.amount,
                )

                print(
                    f"[저장 완료] {args.month} 예산 "
                    f"{args.amount}원"
                )

            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

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

    # summary 명령어 처리
    if args.command == "summary":
        try:
            result = transaction_service.summary_month(
                month=args.month,
                top=args.top,
            )

            if result["count"] == 0:
                print(f"{args.month}: 데이터 없음")
                return 0

            print(f"월별 요약: {result['month']}")
            print(f"총 수입: {result['total_income']}원")
            print(f"총 지출: {result['total_expense']}원")
            print(f"잔액: {result['balance']}원")

                        # 예산 확인 및 사용률 계산
            budget_amount = budget_service.get_budget(args.month)

            if budget_amount is not None:
                total_expense = result["total_expense"]
                usage_rate = total_expense / budget_amount * 100

                print(f"예산: {budget_amount}원")
                print(f"예산 사용률: {usage_rate:.1f}%")

                if total_expense > budget_amount:
                    print("[경고] 월 예산을 초과했습니다!")


            print(f"\n지출 TOP {args.top}")

            if not result["top_categories"]:
                print("지출 내역이 없습니다.")
            else:
                for rank, (name, amount) in enumerate(
                    result["top_categories"],
                    start=1,
                ):
                    print(f"{rank}) {name} {amount}원")

            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

    # list 명령어 처리
# list 명령어 처리
    if args.command == "list":
        if args.limit <= 0:
            print("[오류] --limit은 1 이상의 정수여야 합니다.")
            return 1

        try:
            # 기존에 적용한 스트리밍 개선 코드를 유지
            transactions = heapq.nlargest(
                args.limit,
                transaction_repository.iter_transactions(),
                key=lambda transaction: (
                    transaction.date,
                    transaction.id,
                ),
            )

            count = 0

            for transaction in transactions:
                print(
                    f"{transaction.id} | {transaction.date} | "
                    f"{transaction.type} | {transaction.category} | "
                    f"{transaction.amount} | {transaction.memo}"
                )
                count += 1

            if count == 0:
                print("거래 내역이 없습니다.")

            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

        # export 명령어 처리
    
    if args.command == "export":
        try:
            # 1. 조회 조건 검증
            if args.month:
                try:
                    parsed_month = date.fromisoformat(
                        args.month + "-01"
                    )
                except ValueError:
                    raise ValueError(
                        "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
                    ) from None

                if parsed_month.strftime("%Y-%m") != args.month:
                    raise ValueError(
                        "월은 YYYY-MM 형식이어야 합니다. 예: 2026-10"
                    )

                date_from = args.month + "-01"
                date_to = None

            else:
                if not args.date_from or not args.date_to:
                    raise ValueError(
                        "--from과 --to를 함께 입력해야 합니다."
                    )

                try:
                    date.fromisoformat(args.date_from)
                    date.fromisoformat(args.date_to)
                except ValueError:
                    raise ValueError(
                        "날짜는 YYYY-MM-DD 형식이어야 합니다."
                    ) from None

                date_from = args.date_from
                date_to = args.date_to

                if date_from > date_to:
                    raise ValueError(
                        "시작 날짜는 종료 날짜보다 늦을 수 없습니다."
                    )

            # 2. 출력 파일 경로 준비
            output_path = Path(args.out)
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # 3. CSV 파일 생성
            count = 0

            with output_path.open(
                "w",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                writer = csv.writer(file)

                # CSV 헤더
                writer.writerow([
                    "date",
                    "type",
                    "category",
                    "amount",
                    "memo",
                    "tags",
                ])

                # 거래를 한 건씩 읽으면서 조건에 맞는 데이터만 기록
                for transaction in transaction_repository.iter_transactions():
                    if transaction.date < date_from:
                        continue

                    if date_to and transaction.date > date_to:
                        continue

                    writer.writerow([
                        transaction.date,
                        transaction.type,
                        transaction.category,
                        transaction.amount,
                        transaction.memo,
                        ",".join(transaction.tags or []),
                    ])

                    count += 1

            print(f"[완료] {output_path} ({count} records)")
            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

    # import 명령어 처리
    if args.command == "import":
        try:
            input_path = Path(args.input_file)

            if not input_path.is_file():
                raise ValueError(
                    f"CSV 파일을 찾을 수 없습니다: {input_path}"
                )

            imported = 0
            skipped = 0

            existing_transactions = {
                (transaction.date,
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.memo,
                tuple(transaction.tags or []),)
                for transaction in transaction_service.repository.iter_transactions()}

            with input_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                reader = csv.DictReader(file)

                required_columns = {
                    "date",
                    "type",
                    "category",
                    "amount",
                }

                if not reader.fieldnames or not required_columns.issubset(
                    reader.fieldnames
                ):
                    raise ValueError(
                        "CSV 헤더가 올바르지 않습니다. "
                        "date,type,category,amount 열이 필요합니다."
                    )

                for row in reader:
                    try:
                        # 1. CSV 데이터 읽기
                        transaction_date = row["date"].strip()
                        transaction_type = row["type"].strip()
                        category = row["category"].strip()
                        amount = int(row["amount"])
                        memo = (row.get("memo") or "").strip()

                        tags = [
                            tag.strip()
                            for tag in (row.get("tags") or "").split(",")
                            if tag.strip()
                        ]

                        # 2. 중복 비교용 데이터 생성
                        transaction_key = (
                            transaction_date,
                            transaction_type,
                            category,
                            amount,
                            memo,
                            tuple(tags),
                        )

                        # 3. 이미 존재하는 거래라면 건너뛰기
                        if transaction_key in existing_transactions:
                            skipped += 1
                            continue

                        # 4. 새로운 거래 저장
                        transaction_service.add_transaction(
                            transaction_type=transaction_type,
                            transaction_date=transaction_date,
                            amount=amount,
                            category=category,
                            memo=memo,
                            tags=tags,
                        )

                        # 5. 방금 추가한 거래도 중복 비교 대상에 포함
                        existing_transactions.add(transaction_key)
                        imported += 1

                    except (ValueError, KeyError) as error:
                        skipped += 1
                        print(f"[건너뜀] {error}")

            print(
                f"[완료] imported={imported}, skipped={skipped}"
            )
            return 0

        except (ValueError, OSError) as error:
            print(f"[오류] {error}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
