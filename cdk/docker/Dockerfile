FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1 

ENV PYTHONUNBUFFERED 1

COPY ./requirements /temp/requirements/
COPY ./cdk /cdk

WORKDIR /cdk

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /temp/requirements/dev.txt && \
    rm -rf /temp

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g aws-cdk


COPY ./scripts/cdk-deploy.sh /cdk-deploy.sh
RUN chmod +x /cdk-deploy.sh
    
CMD ["/cdk-deploy.sh"]