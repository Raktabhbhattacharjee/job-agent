from pathlib import Path
from uuid import uuid4

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class FileService:

    @staticmethod
    def save(filename:str ,content:bytes) -> str:
        extension = Path(filename).suffix
        unique_name = f"{uuid4()}{extension}"
        path = UPLOAD_DIR / unique_name
        path.write_bytes(content)
        return str(path)
