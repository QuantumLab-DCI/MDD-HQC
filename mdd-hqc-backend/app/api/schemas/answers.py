from pydantic import BaseModel
from typing import Dict

class AnswerRequest(BaseModel):
    path: str
    answers: Dict[str, str]

class PimToPsmRequest(BaseModel):
    path: str

class PimToPsmAnswerRequest(BaseModel):
    path: str
    answers: Dict[str, str]