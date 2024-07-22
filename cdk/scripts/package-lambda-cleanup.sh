#!/bin/bash

set -e
set -o pipefail
set -u

LAMBDA_DIR="/lambda"

if [ ! -d "$LAMBDA_DIR" ]; then
  echo "Error: The lambda directory does not exist."
  exit 1
fi

# Preserve specific files and directories
find "$LAMBDA_DIR" -mindepth 1 -maxdepth 1 ! -name 'lambda_function.py' ! -name 'requirements' ! -name 'extras' -exec rm -rf {} +

echo "Lambda packaging cleanup completed successfully."