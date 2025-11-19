from flask import Flask, request, jsonify
from flask_cors import CORS
from config.db_config import db, job_posting, job_parser, seekers, recommendations
from utils.drive_downloader import download_drive_to_bytes
from utils.s3_utils import upload_bytes_to_s3, read_s3_file_bytes
from parser_engine.parser import extract_text_from_bytes, parse_content, get_embedding
from recommendation_engine.recommender import rank_jobs

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------------
# 1. ADD JOB POSTING
# ------------------------------------------------------------
@app.route("/add_job_posting", methods=["POST"])
def add_job_posting():
    data = request.json
    drive_link = data["jd_drive_link"]

    # 1. Download file from Google Drive
    file_bytes = download_drive_to_bytes(drive_link)

    # 2. Upload to S3
    key = f"job_descriptions/{data['email']}"
    s3_url = upload_bytes_to_s3(file_bytes, key)

    # 3. Extract text from S3 file
    text = extract_text_from_bytes(file_bytes)

    # 4. Parse and embed
    parsed = parse_content(text)
    embedding = get_embedding(parsed)

    # 5. Store recruiter main details
    job_posting.insert_one({
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "company": data["company"],
        "jd_s3": s3_url
    })

    # 6. Store parsed JD
    job_parser.insert_one({
        "email": data["email"],
        "parsed": parsed,
        "embedding": embedding
    })

    return jsonify({"message": "Job posting uploaded & parsed successfully!"})


# ------------------------------------------------------------
# 2. ADD SEEKER
# ------------------------------------------------------------
@app.route("/add_seeker", methods=["POST"])
def add_seeker():
    data = request.json
    drive_link = data["resume_drive_link"]

    # 1. download bytes
    file_bytes = download_drive_to_bytes(drive_link)

    # 2. upload to S3
    key = f"resumes/{data['email']}"
    s3_url = upload_bytes_to_s3(file_bytes, key)

    seekers.insert_one({
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "resume_s3": s3_url
    })

    return jsonify({"message": "Seeker added successfully"})


# ------------------------------------------------------------
# 3. RECOMMEND JOBS
# ------------------------------------------------------------
@app.route("/recommend_jobs", methods=["POST"])
def recommend_jobs():
    email = request.json["email"]

    user = seekers.find_one({"email": email})
    if not user:
        return jsonify({"error": "Seeker not found"}), 404

    # fetch resume from S3
    resume_bytes = read_s3_file_bytes(user["resume_s3"])

    # parse resume
    text = extract_text_from_bytes(resume_bytes)
    parsed_resume = parse_content(text)
    resume_embedding = get_embedding(parsed_resume)

    # fetch all jobs
    jobs = job_parser.find()
    job_dict = {j["email"]: j["embedding"] for j in jobs}

    # rank similarity
    ranked = rank_jobs(resume_embedding, job_dict)

    results = []
    for recruiter_email, score in ranked:
        post = job_posting.find_one({"email": recruiter_email})
        results.append({
            "company": post["company"],
            "recruiter_email": recruiter_email,
            "name": post["name"],
            "phone": post["phone"],
            "jd_s3": post["jd_s3"],
            "similarity_score": float(score)
        })

    return jsonify(results)


# ------------------------------------------------------------
# 4. APPLY JOB
# ------------------------------------------------------------
@app.route("/apply_job", methods=["POST"])
def apply_job():
    data = request.json

    recommendations.insert_one({
        "seeker_email": data["seeker_email"],
        "recruiter_email": data["recruiter_email"],
        "resume_s3": data["resume_s3"],
        "jd_s3": data["jd_s3"]
    })

    return jsonify({"message": "Application stored"})


# ------------------------------------------------------------
# 5. FETCH TOP CANDIDATES
# ------------------------------------------------------------
@app.route("/top_candidates", methods=["POST"])
def top_candidates():
    recruiter_email = request.json["email"]

    links = recommendations.find({"recruiter_email": recruiter_email})

    result = []
    for rec in links:
        seeker = seekers.find_one({"email": rec["seeker_email"]})

        result.append({
            "name": seeker["name"],
            "email": seeker["email"],
            "phone": seeker["phone"],
            "resume_s3": seeker["resume_s3"]
        })

    return jsonify(result)


# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
