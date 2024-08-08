from pydantic import BaseModel
from typing import List

class QuestionAnswer(BaseModel):
    question: str
    answer: List[str]
    rating: str

class QuestionResponse(BaseModel):
    id: str
    question: str
    answer: List[str]
    rating: str

class SimilarQuestionResponse(BaseModel):
    question: str
    similar_questions: List[str]
