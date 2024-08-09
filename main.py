import os
from typing import List

from fastapi import FastAPI, HTTPException

from pdf_extractor import extract_text_from_pdf, extract_seller_from_transcript, extract_questions_by_speaker, \
    parse_transcript, get_questions
from question_processor import get_question_clusters, rate_answers
from database_manager import MongoDBManager
from models import QuestionAnswer, QuestionResponse, SimilarQuestionResponse
from bson import ObjectId

app = FastAPI()

db_manager = MongoDBManager()

@app.post("/process_pdfs/")
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

@app.get("/top_questions/", response_model=List[QuestionResponse])
def get_top_questions():
    questions = db_manager.get_top_questions()
    return [{"id": str(q["_id"]), "question": q["question"], "answer": q["answer"], "rating": q["rating"]} for q in
            questions]



@app.delete("/questions/{question_id}/")
def delete_question(question_id: str):
    result = db_manager.delete_question(ObjectId(question_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


@app.delete("/questions/")
def delete_all_questions():
    db_manager.delete_all_questions()
    return {"message": "All questions deleted successfully"}

@app.get("/allquestions/")
def get_all_questions_man():
    questions = db_manager.get_all_questions()
    return [{"id": str(q["_id"]), "similar_question": q["questions_and_answers"]} for q in
            questions]
