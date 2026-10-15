
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN unset PIP_REQUIRE_HASHES && python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir --retries 10 --timeout 300 --index-url https://pypi.org/simple -r requirements.txt


COPY . .


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]