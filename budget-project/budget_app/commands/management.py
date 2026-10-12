def handle_category(args, category_service, transaction_repository):
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


def handle_budget(args, budget_service):
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