#!/bin/bash

set -e
set -o pipefail
set -u

LAMBDA_DIR="/lambda"
REQUIREMENTS_DIR="$LAMBDA_DIR/requirements"
REQUIREMENTS_FILE="requirements.txt"

if [ ! -d "$LAMBDA_DIR" ]; then
  echo "Error: The lambda directory does not exist."
  exit 1
fi

if [ ! -d "$REQUIREMENTS_DIR" ]; then
  echo "Error: The requirements directory does not exist in lambda directory."
  exit 1
fi

pip install --target "$LAMBDA_DIR" -r "$REQUIREMENTS_DIR/$REQUIREMENTS_FILE"


echo "Lambda packaging completed successfully."