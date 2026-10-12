def handle_update(args, transaction_service):
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