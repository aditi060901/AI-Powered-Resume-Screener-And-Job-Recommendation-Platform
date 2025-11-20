import pdfplumber
import docx2txt
from io import BytesIO
import re
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_bytes(file_bytes):
    try:
        # Try PDF
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
            if text:
                return text
    except:
        pass

    # Fallback: assume DOCX
    try:
        return docx2txt.process(BytesIO(file_bytes))
    except:
        return ""

ALL_SKILLS = [
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", 
    "rust", "php", "kotlin", "swift", "ruby", "scala",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite",
    "mariadb", "dynamodb", "cassandra",

    # Web Frameworks
    "react", "angular", "vue", "node", "nodejs", "express",
    "django", "flask", "fastapi", "spring", "spring boot","html","css",

    # AI / ML / Data
    "tensorflow", "pytorch", "keras", "sklearn", "scikit-learn",
    "spacy", "transformers", "data analysis","nltk","pillow",
    "nlp", "opencv", "machine learning", "scipy", "generative ai", "data analytics",
    "deep learning","data preprocessing","exploratory data analysis","artificial intelligence","ai","ml","natural language processing",

    # Cloud / DevOps
    "aws", "s3", "ec2", "lambda", "gcp", "azure", "docker",
    "kubernetes", "helm",

    # Tools
    "git", "github", "jira", "tableau", "power bi",

    "agile", "saas", "paas", "rag","linux","data structures and algorithm","dsa","ci","cd"
]


def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in ALL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found_skills.append(skill)

    return list(set(found_skills))  # remove duplicates


def extract_education_dict(text):

    clean = text.lower()


    edu_map = {
        "10th": ["10th", "ssc","secondary school"],
        "12th": ["12th", "hsc","higher secondary"],
        "btech": ["b.tech", "btech", "b tech", "bachelor"],
        "mtech": ["m.tech", "mtech", "m tech", "master"],
        "ug": ["ug", "undergraduate"],
        "pg": ["pg", "postgraduate"]
    }

    # Regex for scores: percent or CGPA/GPA
    score_regex = r"(\d{1,2}\.?\d?\s*%|\d\.?\d*\s*(cgpa|gpa))"

    education = {}

    for key, variants in edu_map.items():
        for v in variants:
            # Pattern: <education_name> ... <score>
            pattern = v + r"[^\n:]*?(?:[:\- ]+)?\s*" + score_regex

            match = re.search(pattern, clean, flags=re.I)

            if match:
                score = match.group(1).replace(" ", "")
                education[key] = score
                break  

    return education



def parse_content(text):
    text = text.lower()

    skills = extract_skills(text)
    education = extract_education_dict(text)
    exp = re.findall(r"(\d+ years|\d+ year)", text)
    certs = re.findall(r"(certificate|certified)", text)

    return {
        "skills": skills,
        "education": education,
        "experience": list(set(exp)),
        "certifications": list(set(certs))
    }


def get_embedding(parsed):

    edu_text = " ".join([f"{k}:{v}" for k, v in parsed["education"].items()])

    combined = (
        " ".join(parsed["skills"]) + " " +
        edu_text + " " +
        " ".join(parsed["experience"]) + " " +
        " ".join(parsed["certifications"])
    )
    return model.encode([combined])[0].tolist()
