from pydantic import BaseModel
from typing import List

class SimilarQuestionResponse(BaseModel):
    similar_question_index:int
    questions_count: int
    questions: List[str]

class QuestionAnswerResponse(BaseModel):
    id: str
    question: str
    answer: str
    rating: str

