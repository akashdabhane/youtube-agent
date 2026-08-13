from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    query: str
    url: Optional[str] = None
    user_id: Optional[str] = None


