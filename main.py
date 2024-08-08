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
def process_pdfs(limit = 10):
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
                all_questions_dict[question].append(questions_dict[question])
    clusters = get_question_clusters(list(all_questions_dict.keys()))
    most_common_questions = list(sorted(clusters, key = lambda cluster:len(cluster)))
    top_5_questions = []
    for index,questions in enumerate(most_common_questions[-5:]):
        similar_question = {
            "similar_question":index+1,
            "questions_and_answers": []
        }
        ratings = rate_answers(questions,all_questions_dict[question])
        for qid,question in enumerate(questions):
            data = {
                f"question":question,
                "answers": all_questions_dict[question],
                "ratings": ratings[question]
            }
            similar_question["questions_and_answers"].append(data)
            top_5_questions.append(similar_question)
            break
    db_manager.insert_question_answer(top_5_questions)
    response = []
    for question in most_common_questions[-limit:]:
        response.append(
            {
                "questions":question,
                "count":len(question)
            }
        )
    return response


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
