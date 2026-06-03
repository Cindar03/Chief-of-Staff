FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV DATABASE_URL=sqlite:///data/chief_of_staff.db
EXPOSE 8000
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000"]
