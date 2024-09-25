FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/wait-for-it.sh

ENV PYTHONPATH="/app:${PYTHONPATH}"

# Use the wait-for-it script to wait for the database to be ready before starting
CMD ["/app/wait-for-it.sh", "db:5432", "--", "python", "manager.py"]
