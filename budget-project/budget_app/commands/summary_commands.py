
def handle_summary(args, transaction_service, budget_service):
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