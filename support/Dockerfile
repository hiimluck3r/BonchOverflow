FROM python:3.9-slim

LABEL authors="hiimluck3r"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ~/BonchOverflowSupport

COPY . ./support
RUN pip install --no-cache-dir -r ./support/requirements_support.txt

CMD ["python", "-m", "support"]
