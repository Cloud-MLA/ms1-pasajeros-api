FROM python:3.12-slim

ENV PORT=8001 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ROOT_PATH=

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --root-path \"${ROOT_PATH}\""]