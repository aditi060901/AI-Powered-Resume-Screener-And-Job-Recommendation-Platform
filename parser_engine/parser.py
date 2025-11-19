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


def parse_content(text):
    text = text.lower()

    skills = re.findall(r"(python|java|react|ml|nlp|docker|flask)", text)
    education = re.findall(r"(b\.tech|m\.tech|bachelor|master)", text)
    exp = re.findall(r"(\d+ years|\d+ year)", text)
    certs = re.findall(r"(certificate|certified)", text)

    return {
        "skills": list(set(skills)),
        "education": list(set(education)),
        "experience": list(set(exp)),
        "certifications": list(set(certs))
    }


def get_embedding(parsed):
    combined = (
        " ".join(parsed["skills"]) + " " +
        " ".join(parsed["education"]) + " " +
        " ".join(parsed["experience"]) + " " +
        " ".join(parsed["certifications"])
    )
    return model.encode([combined])[0].tolist()
