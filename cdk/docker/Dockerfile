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

COPY ./scripts/setup.sh /setup.sh
COPY ./scripts/setup-aws-cred.sh /setup-aws-cred.sh
COPY ./scripts/package-lambda.sh /package-lambda.sh
COPY ./scripts/copy-media-2-s3.sh /copy-media-2-s3.sh
COPY ./scripts/startup.sh /startup.sh
RUN chmod +x /setup.sh /setup-aws-cred.sh /package-lambda.sh /copy-media-2-s3.sh /startup.sh

ENTRYPOINT ["/setup.sh"]

WORKDIR /cdk

COPY ./scripts/cdk-deploy.sh /cdk-deploy.sh
RUN chmod +x /cdk-deploy.sh

# for mp3 files
COPY ./media /temp/media/

CMD ["/startup.sh"]