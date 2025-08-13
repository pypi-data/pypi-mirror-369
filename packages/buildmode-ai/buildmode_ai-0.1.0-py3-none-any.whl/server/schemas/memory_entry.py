from pydantic import BaseModel
from typing import Optional


class MemoryEntry(BaseModel):
    file_path: str
    summary: Optional[str] = None
    full_text: Optional[str] = None
    notes: Optional[str] = None
