import csv
from datetime import date
from pathlib import Path


def handle_export(args, transaction_repository) -> int:
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

            writer.writerow([
                "date",
                "type",
                "category",
                "amount",
                "memo",
                "tags",
            ])

            # 거래를 한 건씩 읽으며 조건에 맞는 데이터 기록
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

def handle_import(args, transaction_service) -> int:
    try:
        input_path = Path(args.input_file)

        if not input_path.is_file():
            raise ValueError(
                f"CSV 파일을 찾을 수 없습니다: {input_path}"
            )

        imported = 0
        skipped = 0

        existing_transactions = {
            (
                transaction.date,
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.memo,
                tuple(transaction.tags or []),
            )
            for transaction in (
                transaction_service.repository.iter_transactions()
            )
        }

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
