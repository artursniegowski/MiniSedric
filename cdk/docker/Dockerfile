FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1 

ENV PYTHONUNBUFFERED 1

COPY ./requirements /temp/requirements/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /temp/requirements/dev.txt && \
    rm -rf /temp

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g aws-cdk-local aws-cdk

COPY ./cdk /cdk
COPY ./lambda /lambda
COPY ./scripts /scripts

RUN chmod -R +x /scripts

ENV PATH="/scripts:$PATH"

ENTRYPOINT ["setup.sh"]

WORKDIR /cdk

# for mp3 files
COPY ./media /temp/media/

CMD ["startup.sh"]