
def handle_search(args, transaction_service):
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
