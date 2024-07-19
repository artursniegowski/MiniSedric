#!/bin/bash

set -e
set -o pipefail
set -u

cd ..

LAMBDA_DIR="lambda"

if [ ! -d "$LAMBDA_DIR" ]; then
  echo "Error: The lambda directory does not exist."
  exit 1
else
  echo "The directory 'lambda' already exists."
fi

cd "$LAMBDA_DIR"

pip install --target . -r requirements.txt


echo "Lambda packaging completed successfully."