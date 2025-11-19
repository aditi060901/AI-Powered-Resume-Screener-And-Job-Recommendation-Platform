import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(a, b):
    a = np.array(a).reshape(1, -1)
    b = np.array(b).reshape(1, -1)
    return cosine_similarity(a, b)[0][0]

def rank_jobs(resume_emb, job_dict):
    scores = []
    for recruiter_email, embedding in job_dict.items():
        score = compute_similarity(resume_emb, embedding)
        scores.append((recruiter_email, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
