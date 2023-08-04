FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ~/BonchOverflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY bot ./bot

CMD ["python", "-m", "bot"]