#!/bin/bash

set -e
set -o pipefail
set -u

cdklocal bootstrap -v --output ./cdk.local.out
cdklocal deploy -v --require-approval never --output ./cdk.local.out