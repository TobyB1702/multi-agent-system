from pydantic import BaseModel
from typing import Optional

class AgentResponse(BaseModel):
    final_answer: str
    session_dir: Optional[str] = None