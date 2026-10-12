
def handle_add(args, transaction_service):
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
