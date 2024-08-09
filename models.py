from pydantic import BaseModel
from typing import List

class SimilarQuestionResponse(BaseModel):
    similar_question_index:str
    questions_count: str
    questions: List[str]

class QuestionAnswerResponse(BaseModel):
    id: str
    question: str
    answer: List[str]
    rating: str

