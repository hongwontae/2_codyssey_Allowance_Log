
from budget_app.cli import main


if __name__ == "__main__":
    try :
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError) :
        print("keyboard - interrupt and EOFError")
    