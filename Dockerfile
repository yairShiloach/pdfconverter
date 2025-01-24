FROM python:3.9

# Install poppler
RUN apt-get update && apt-get install -y poppler-utils

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]