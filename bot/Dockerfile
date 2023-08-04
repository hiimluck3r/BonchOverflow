FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ~/BonchOverflow

COPY . ./bot
RUN pip install --no-cache-dir -r ./bot/requirements.txt

CMD ["python", "-m", "bot"]