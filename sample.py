from sentence_transformers import SentenceTransformer, util


def rate_answers(questions, answers_list):
    # Load pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose another model if needed

    # Initialize results dictionary
    results = {}

    for question, answers in zip(questions, answers_list):
        # Compute embeddings for the question and answers
        question_embedding = model.encode(question, convert_to_tensor=True)
        answer_embeddings = model.encode(answers, convert_to_tensor=True)

        # Compute cosine similarity between the question and each answer
        similarities = util.pytorch_cos_sim(question_embedding, answer_embeddings)

        # Calculate length scores as a simple heuristic (optional)
        max_len = max(len(answer.split()) for answer in answers)  # Find the max length for normalization
        length_scores = [len(answer.split()) / max_len for answer in answers]

        # Function to rate the answers based on similarity and length heuristic
        def rate_answer(similarity, length_score):
            if similarity > 0.8 and length_score > 0.7:
                return "Best"
            elif similarity > 0.6:
                return "Good"
            else:
                return "Average"

        # Rate each answer and store results
        ratings = []
        for i, similarity in enumerate(similarities[0]):
            rating = rate_answer(similarity.item(), length_scores[i])
            ratings.append(rating)

        results[question] = ratings

    return results


# Example usage:
questions = [
    "What are the benefits of cloud computing?",
    "How does machine learning work?"
]

answers_list = [
    [
        "Cloud computing provides scalability, flexibility, and cost efficiency.",
        "It is a good technology for businesses.",
        "Cloud computing allows organizations to quickly scale their infrastructure, reduce costs by paying for what they use, and increase flexibility by enabling remote work and collaboration."
    ],
    [
        "Machine learning is a field of artificial intelligence.",
        "It involves algorithms that learn from data.",
        "Machine learning uses statistical methods to enable computers to learn from data without being explicitly programmed."
    ]
]

ratings = rate_answers(questions, answers_list)
for question, rating in ratings.items():
    print(f"Question: {question}")
    for i, r in enumerate(rating):
        print(f"  Answer {i + 1}: {r}")
