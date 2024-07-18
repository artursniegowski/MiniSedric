FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1 

ENV PYTHONUNBUFFERED 1

COPY ./requirements /temp/requirements/
COPY ./app /app

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /temp/requirements/base.txt && \
    rm -rf /temp

# CMD ["python", "lambda_function.py"]