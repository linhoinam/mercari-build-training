FROM python:3.12-alpine

WORKDIR /app
RUN apk add --no-cache sqlite

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY db/items.sql /app/db/items.sql
COPY db/mercari.sqlite3 /app/db/mercari.sqlite3

CMD sqlite3 /app/db/mercari.sqlite3 < /app/db/items.sql && \
    uvicorn main:app --host 0.0.0.0 --port 9000