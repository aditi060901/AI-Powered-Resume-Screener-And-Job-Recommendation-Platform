<<<<<<< HEAD:DockerFile
FROM python:3.12.6-slim

WORKDIR /app

# Install required system packages (SpaCy dependency)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Add required spaCy model ----
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 5000

=======
FROM python:3.12.6-slim

WORKDIR /app

# Install required system packages (SpaCy dependency)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Add required spaCy model ----
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 5000

>>>>>>> 72349b680ffe7e4d2d0140405767b51b1abaa519:Dockerfile
CMD ["python", "app.py"]