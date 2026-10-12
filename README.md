# 나만의 용돈 기입장

## 1. 프로젝트 소개

Python과 파일 입출력을 활용한 콘솔 기반 가계부 프로그램입니다.

수입과 지출을 기록하고, 거래 검색 및 수정·삭제, 월별 요약, 예산 관리, 카테고리 관리, CSV 가져오기·내보내기 기능을 제공합니다.

## 2. 개발 환경

- Python 3.10 이상
- Python 표준 라이브러리
- JSONL 파일 기반 데이터 저장
- `unittest`를 이용한 자동 테스트

## 3. 프로젝트 구조

```text
budget-project/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   ├── repository.py
│   └── services.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_repository.py
│   └── test_services.py
├── data/
├── README.md
└── .gitignore
```

- `models.py`: 거래 데이터 모델 정의
- `repository.py`: 파일 저장 및 조회
- `services.py`: 거래, 카테고리, 예산 관련 비즈니스 로직
- `cli.py`: 명령어와 사용자 입력 처리
- `__main__.py`: 프로그램 실행 진입점
- `tests/`: 자동 테스트 코드

## 4. 실행 방법

프로젝트 루트 디렉터리에서 실행합니다.

```bash
python -m budget_app --help
```

기본 저장 폴더는 `./data`이며, `--data-dir` 옵션으로 변경할 수 있습니다.

```bash
python -m budget_app --data-dir ./my_data list
```

## 5. 주요 기능

| 명령어 | 기능 |
| --- | --- |
| `add` | 거래 추가 |
| `list` | 거래 목록 조회 |
| `search` | 조건별 거래 검색 |
| `summary` | 월별 수입·지출 요약 |
| `budget` | 월별 예산 설정 및 조회 |
| `category` | 카테고리 관리 |
| `update` | 거래 수정 |
| `delete` | 거래 삭제 |
| `import` | CSV 거래 가져오기 |
| `export` | CSV 거래 내보내기 |

## 6. CSV 가져오기 및 내보내기

CSV 파일은 UTF-8 인코딩과 헤더를 사용합니다.

| 컬럼 | 필수 여부 | 설명 |
| --- | --- | --- |
| `date` | 필수 | 거래 날짜 (`YYYY-MM-DD`) |
| `type` | 필수 | `income` 또는 `expense` |
| `category` | 필수 | 등록된 카테고리 |
| `amount` | 필수 | 양의 정수 금액 |
| `memo` | 선택 | 거래 메모 |
| `tags` | 선택 | 쉼표로 구분한 태그 |

예시:

```csv
date,type,category,amount,memo,tags
2026-10-10,expense,food,5000,점심,meal
2026-10-11,income,salary,100000,용돈,income
```

CSV 가져오기:

```bash
python -m budget_app import --from import.csv
```

CSV 내보내기:

```bash
python -m budget_app export --out export.csv --month 2026-10
```

잘못된 거래 행이나 중복 거래는 건너뛸 수 있으며, 처리 결과에서 등록 및 건너뛴 건수를 확인합니다.

## 7. 데이터 저장

프로그램 데이터는 JSONL 형식으로 저장합니다.

- `transactions.jsonl`: 거래 내역
- `categories.jsonl`: 카테고리 목록
- `budgets.jsonl`: 월별 예산

각 파일은 한 줄에 하나의 JSON 객체를 저장합니다. 프로그램을 종료해도 데이터가 유지됩니다.

## 8. 테스트 실행

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python -m unittest discover -s tests -v
```

테스트 결과의 마지막에 `OK`가 표시되면 모든 테스트가 통과한 것입니다.
