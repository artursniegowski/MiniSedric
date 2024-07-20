#!/bin/bash

# Run the setup AWS credentials script
/setup-aws-cred.sh

# Execute the main process (optional)
exec "$@"