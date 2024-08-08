import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import pdfplumber

def extract_text_from_pdf(pdf_path):
    print(f"Extracting pdf text from {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text
def parse_transcript(transcript):
    # Regular expression pattern to match the time, speaker, and message
    pattern = r'(\d{1,2}:\d{2}) \| (\w+)\n(.+?)(?=\n\d{1,2}:\d{2} \| |\Z)'
    # Find all matches in the transcript
    matches = re.findall(pattern, transcript, re.DOTALL)
    # Format the output as a list of tuples
    result = [(time, speaker, message.strip()) for time, speaker, message in matches]
    return result

def get_questions(modified_transcript):
    question = ''
    questions_dict = {}
    for timestamp,person,text in modified_transcript:
        if question:
            if question not in questions_dict:
                questions_dict[question] = []
            questions_dict[question].append(text) #answer
            question = ''
        if '?' in text and person=='Nathan': #person=='seller':
            question = text
    if question and question not in questions_dict:
        questions_dict[question] = []
    return questions_dict

def get_question_clusters(questions):
    # Step 2: Convert filtered strings to feature vectors using TfidfVectorizer
    vectorizer = TfidfVectorizer().fit_transform(questions)
    vectors = vectorizer.toarray()
    # Step 3: Compute cosine similarity between the vectors
    cosine_sim = cosine_similarity(vectors)
    # Threshold to decide if texts are similar (adjust as needed)
    threshold = 0.45
    # Function to group similar strings based on cosine similarity
    def cluster_strings(sim_matrix, threshold):
        clusters = []
        visited = set()
        for idx in range(sim_matrix.shape[0]):
            if idx not in visited:
                # Find all strings similar to the current one
                similar_indices = np.where(sim_matrix[idx] > threshold)[0]
                cluster = [questions[i] for i in similar_indices]
                clusters.append(cluster)
                visited.update(similar_indices)
        return clusters
    # Step 4: Get clusters of similar strings
    clusters = cluster_strings(cosine_sim, threshold)
    return clusters

all_questions_dict = {}
folder_path = 'calls/'
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        file_path = os.path.join(folder_path, filename)
        transcript = extract_text_from_pdf(file_path)
        # Parse the transcript
        parsed_transcript = parse_transcript(transcript)
        questions_dict = get_questions(parsed_transcript)
        for question in questions_dict:
            if question not in all_questions_dict:
                all_questions_dict[question] = []
            all_questions_dict[question].append(questions_dict[question])
clusters = get_question_clusters(list(all_questions_dict.keys()))

common_questions = []
# Print the result
for cluster in clusters:
    if len(cluster)>2:
        common_questions.append((len(cluster),cluster))
    print(cluster)
common_questions = list(sorted(common_questions,reverse=True))[:10]
print("COMMON QUESTIONS")
print(common_questions)
questions_answers = []
print("Top questions",len(common_questions))
for count,cluster in common_questions:
    print(count)
    # for que in cluster:
    #     questions_answers.append((que,all_questions_dict[que]))
    # break
print(questions_answers[:10])
        # print("Question:",que)
        # print("Answers:",len(all_questions_dict[que]),all_questions_dict[que])
# print(clusters)

