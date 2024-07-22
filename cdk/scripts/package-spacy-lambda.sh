#!/bin/bash

set -e
set -o pipefail
set -u


LAMBDA_DIR="/lambda"
REQUIREMENTS_DIR="$LAMBDA_DIR/requirements"
REQUIREMENTS_FILE="spacy-requirements.txt"
SPACY_MODEL="en_core_web_md"

if [ ! -d "$LAMBDA_DIR" ]; then
  echo "Error: The lambda directory does not exist."
  exit 1
fi

if [ ! -d "$REQUIREMENTS_DIR" ]; then
  echo "Error: The requirements directory does not exist in lambda directory."
  exit 1
fi


pip install --target "$LAMBDA_DIR" -r "$REQUIREMENTS_DIR/$REQUIREMENTS_FILE" --no-cache-dir
# MODEL_URL=$(python -m spacy info "$SPACY_MODEL" --url)
MODEL_URL=$(PYTHONPATH="$LAMBDA_DIR" python -m spacy info "$SPACY_MODEL" --url)
pip install --target "$LAMBDA_DIR" "$MODEL_URL" --no-cache-dir


echo "Lambda packaging completed for spacy - NLP successfully."