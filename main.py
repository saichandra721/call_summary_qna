import os
from typing import List

from fastapi import FastAPI, HTTPException

from pdf_extractor import extract_text_from_pdf, extract_seller_from_transcript, extract_questions_by_speaker, \
    parse_transcript, get_questions
from question_processor import get_question_clusters, rate_answers
from database_manager import MongoDBManager
from models import SimilarQuestionResponse, QuestionAnswerResponse
from bson import ObjectId

app = FastAPI()

db_manager = MongoDBManager()

@app.post("/process_pdfs/",  response_model=List[SimilarQuestionResponse])
def process_pdfs(limit:int = 10):
    print("Entered process pdfs")
    all_questions_dict = {}
    folder_path = 'calls/'
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            transcript = extract_text_from_pdf(file_path)
            parsed_transcript = parse_transcript(transcript)
            questions_dict = get_questions(parsed_transcript)
            for question in questions_dict:
                if question not in all_questions_dict:
                    all_questions_dict[question] = []
                all_questions_dict[question].extend(questions_dict[question])
    clusters = get_question_clusters(list(all_questions_dict.keys()))
    most_common_questions = list(sorted(clusters, key = lambda cluster:len(cluster)))
    top_5_best_questions = []
    top_5_good_questions = []
    top_5_average_questions = []
    similar_questions = []
    for index,questions in enumerate(most_common_questions):
        similar_question = {
            "similar_question_index":index+1,
            "questions_count": len(questions),
            "questions": questions
        }
        similar_questions.append(similar_question)
        for qid,question in enumerate(questions):
            answers = all_questions_dict[question]
            if not answers:
                continue
            ratings = rate_answers(question,answers)
            for answer,rating in zip(answers,ratings):
                qna = {
                    "question":question,
                    "answer":answer,
                    "rating":rating
                }
                if rating=="BEST" and len(top_5_best_questions)<5:
                    top_5_best_questions.append(qna)
                elif rating=="GOOD" and len(top_5_good_questions)<5:
                    top_5_good_questions.append(qna)
                elif rating=="AVERAGE" and len(top_5_average_questions)<5:
                    top_5_average_questions.append(qna)
    top_5 = top_5_best_questions+top_5_good_questions+top_5_average_questions
    # db_manager.insert_question_answer(top_5[:5])
    return similar_questions[:limit]

@app.get("/top5_questions/", response_model=List[QuestionAnswerResponse])
def get_top_questions():
    questions_and_answers = db_manager.get_top_questions()
    response = [
        {
            "id": str(qna["_id"]),
            "question": qna["question"],
            "answer": qna["answer"],
            "rating": qna["rating"]
        }
        for qna in questions_and_answers
    ]
    return response
