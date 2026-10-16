import json

from pathlib import Path
from collections.abc import Iterator

from budget_app.models import Transaction


class TransactionRepository:
    def __init__(self, file_path: Path):
        self.file_path = file_path

        # 저장 폴더가 없으면 생성
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # 저장 파일이 없으면 생성
        self.file_path.touch(exist_ok=True)

    def iter_transactions(self) -> Iterator[Transaction]:
        """거래 내역을 한 건씩 읽는다."""

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        if not isinstance(data, dict):
                            raise ValueError(
                                "거래 데이터는 JSON 객체여야 합니다."
                            )

                        transaction = Transaction(**data)

                    except (json.JSONDecodeError, TypeError, KeyError, ValueError):
                        raise ValueError(
                            f"거래 파일 {self.file_path}의 "
                            f"{line_number}번째 줄이 올바르지 않습니다. "
                            "JSON 형식과 거래 필드를 확인하세요."
                        ) from None

                    yield transaction

        except UnicodeDecodeError:
            raise ValueError(
                f"거래 파일 {self.file_path}의 문자 인코딩이 올바르지 않습니다. "
                "UTF-8 파일인지 확인하세요."
            ) from None

    def add(self, transaction: Transaction) -> None:
        """거래 한 건을 JSONL 파일에 추가한다."""
        data = {
            "id": transaction.id,
            "type": transaction.type,
            "date": transaction.date,
            "amount": transaction.amount,
            "category": transaction.category,
            "memo": transaction.memo,
            "tags": transaction.tags or [],
        }

        # 기존 파일의 마지막 줄이 줄바꿈으로 끝나는지 확인
        with self.file_path.open("rb+") as file:
            file.seek(0, 2)
            file_size = file.tell()

            if file_size > 0:
                file.seek(-1, 2)
                last_byte = file.read(1)

                if last_byte != b"\n":
                    file.write(b"\n")

            file.write(
                (
                    json.dumps(data, ensure_ascii=False) + "\n"
                ).encode("utf-8")
            )
            
    def delete(self, transaction_id: str) -> bool:
        """ID에 해당하는 거래를 삭제한다."""

        temp_path = self.file_path.with_suffix(".tmp")
        found = False

        try:
            with self.file_path.open("r", encoding="utf-8") as source:
                with temp_path.open("w", encoding="utf-8") as target:
                    for line_number, line in enumerate(source, start=1):
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)

                            if not isinstance(data, dict) or "id" not in data:
                                raise ValueError("거래 데이터에 id가 없습니다.")

                        except (json.JSONDecodeError, ValueError):
                            raise ValueError(
                                f"거래 파일의 {line_number}번째 줄이 "
                                "손상되었습니다. 파일을 확인하세요."
                            ) from None

                        if data["id"] == transaction_id:
                            found = True
                            continue

                        target.write(
                            json.dumps(data, ensure_ascii=False) + "\n"
                        )

            if not found:
                return False

            # 임시 파일 작성이 성공한 경우에만 원본 교체
            temp_path.replace(self.file_path)
            return True

        finally:
            # 성공적으로 교체했다면 파일이 이미 없어졌으므로 아무 일도 하지 않음
            # 실패했다면 남은 임시 파일을 정리
            temp_path.unlink(missing_ok=True)

    def update(self, transaction: Transaction) -> bool:
        """기존 거래를 수정한다. 대상 ID가 없으면 False를 반환한다."""

        temp_path = self.file_path.with_suffix(".tmp")
        found = False

        try:
            with self.file_path.open("r", encoding="utf-8") as source:
                with temp_path.open("w", encoding="utf-8") as target:
                    for line_number, line in enumerate(source, start=1):
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)

                            if not isinstance(data, dict) or "id" not in data:
                                raise ValueError("거래 데이터에 id가 없습니다.")

                        except (json.JSONDecodeError, ValueError):
                            raise ValueError(
                                f"거래 파일의 {line_number}번째 줄이 "
                                "손상되었습니다. 파일을 확인하세요."
                            ) from None

                        if data["id"] == transaction.id:
                            data = {
                                "id": transaction.id,
                                "type": transaction.type,
                                "date": transaction.date,
                                "amount": transaction.amount,
                                "category": transaction.category,
                                "memo": transaction.memo,
                                "tags": transaction.tags or [],
                            }
                            found = True

                        target.write(
                            json.dumps(data, ensure_ascii=False) + "\n"
                        )

            if not found:
                return False

            # 모든 줄을 정상적으로 작성한 뒤에만 원본 교체
            temp_path.replace(self.file_path)
            return True
        
        finally:
            temp_path.unlink(missing_ok=True)

