#!/bin/bash

# set -e
# set -o pipefail
# set -u

# #################################################
# echo "AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}"
# echo "AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}"
# echo "AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
# ##################################################


# aws configure set aws_access_key_id "${AWS_ACCESS_KEY_ID}" --profile dev-localstack
# aws configure set aws_secret_access_key "${AWS_SECRET_ACCESS_KEY}" --profile dev-localstack
# # aws configure set endpoint_url "${AWS_ENDPOINT_URL}" --profile localstack
# aws configure set region "${AWS_DEFAULT_REGION}" --profile dev-localstack
# aws configure set output json --profile dev-localstack


# echo "Setting AWS credentials: COMPLETED"
# #########################
# aws configure list
# #########################
# echo "#### CREDENTIALS ######"
# cat ~/.aws/credentials
# echo "#### CONFIG ######"
# cat ~/.aws/config

# echo "#### check cdklocal ls -v - START ######"
# cdklocal ls -v
# echo "#### check cdklocal ls -v - EDN ######"
# echo "#### aws sts get-caller-identity START ######"
# aws sts get-caller-identity --endpoint-url http://localhost:4566 --profile dev-localstack
# echo "#### aws sts get-caller-identity EDN ######"
# echo "#### create secret - START ######"
# aws --endpoint-url http://localhost:4566 --profile dev-localstack secretsmanager create-secret --name TestSecret
# echo "#### create secret  END ######"
# echo "#### Check ######"
# aws --endpoint-url http://localhost:4566 --profile dev-localstack secretsmanager list-secrets
# echo "#### Check ######"