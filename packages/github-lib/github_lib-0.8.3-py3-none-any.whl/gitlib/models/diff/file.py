
from pydantic import BaseModel


class DiffFile(BaseModel):
    content: str
    path: str
    size: int
