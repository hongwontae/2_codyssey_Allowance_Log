import json
from collections.abc import Iterator
from pathlib import Path


class CategoryRepository:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def iter_categories(self) -> Iterator[str]:
        """등록된 카테고리를 한 개씩 반환한다."""
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                data = json.loads(line)
                yield data["name"]

    def add(self, name: str) -> None:
        """카테고리를 파일에 추가한다."""
        data = {"name": name}

        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    def remove(self, name: str) -> bool:
        """카테고리를 삭제한다. 존재하지 않으면 False를 반환한다."""
        categories = list(self.iter_categories())

        if name not in categories:
            return False

        remaining = [category for category in categories if category != name]

        temp_path = self.file_path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            for category in remaining:
                data = {"name": category}
                file.write(json.dumps(data, ensure_ascii=False) + "\n")

        temp_path.replace(self.file_path)
        return True

