#!/bin/bash

# Run the setup AWS credentials script
/setup-aws-cred.sh

# Run the package Lambda script
/package-lambda.sh

# Execute the main process (optional)
exec "$@"