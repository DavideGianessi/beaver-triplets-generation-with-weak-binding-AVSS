FROM python:3.11-slim
WORKDIR /app
COPY party/ /app/

COPY party/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "party.py"]
