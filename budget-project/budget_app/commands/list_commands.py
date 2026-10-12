import heapq


def handle_list(args, transaction_repository):
    if args.limit <= 0:
        print("[오류] --limit은 1 이상의 정수여야 합니다.")
        return 1

    try:
        # 최신 거래부터 limit 개수만 조회
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