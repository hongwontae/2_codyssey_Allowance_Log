def handle_delete(args, transaction_repository):
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