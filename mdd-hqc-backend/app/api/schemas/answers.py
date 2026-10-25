from pydantic import BaseModel
from typing import Dict, Any

class AnswerRequest(BaseModel):
    path: str
    answers: Dict[str, Any]

class PimToPsmRequest(BaseModel):
    path: str

class PimToPsmAnswerRequest(BaseModel):
    path: str
    answers: Dict[str, str]