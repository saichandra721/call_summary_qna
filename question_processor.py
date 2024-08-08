from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

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

