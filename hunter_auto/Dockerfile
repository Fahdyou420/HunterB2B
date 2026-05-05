FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y wget gnupg xvfb libfontconfig1 libnss3 libgconf-2-4 libnss3-dev libxss1 libasound2 \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install chromium \
    && playwright install-deps

COPY . .

CMD ["python", "main.py"]
