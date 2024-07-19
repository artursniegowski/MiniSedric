#!/bin/bash

set -e
set -o pipefail
set -u

sleep 1

DIRECTORY="/temp/media"
BUCKET="${AWS_S3_BUCKETNAME_MINISEDRIC}"
ENDPOINT_URL="${AWS_ENDPOINT_URL}"


if [ -d "$DIRECTORY" ]; then
    echo "Directory $DIRECTORY exists."
else
    echo "Directory $DIRECTORY does not exist."
    exit 1
fi

MP3_FILES=($DIRECTORY/*.mp3)
if [ ${#MP3_FILES[@]} -eq 0 ]; then
    echo "No MP3 files found in $DIRECTORY."
    exit 1
fi


echo "### COPY MP3s to my S3 bucket -- START ###"
for file in "${MP3_FILES[@]}"; do
    # Extract the filename from the full path
    filename=$(basename "$file")
    
    echo "Uploading $filename to s3://$BUCKET/"
    
    aws --endpoint-url "$ENDPOINT_URL" s3api put-object \
        --bucket "$BUCKET" \
        --key "$filename" \
        --body "$file" \
        --content-type "audio/mpeg"

    if [ $? -eq 0 ]; then
        echo "Successfully uploaded $filename."
    else
        echo "Failed to upload $filename."
    fi
done
echo "### COPY MP3s to my S3 bucket -- END ###"


# aws s3api list-buckets --endpoint-url http://localhost.localstack.cloud:4566
# echo "${AWS_ENDPOINT_URL}"
# echo "### COPY MP3 to my s3 bucket -- START ###"
# # aws --endpoint-url "${AWS_ENDPOINT_URL}" s3 cp /temp/media/sample.mp3 s3://MiniSedricBucket/
# aws --endpoint-url "${AWS_ENDPOINT_URL}" s3api put-object --bucket "${AWS_S3_BUCKETNAME_MINISEDRIC}" --key sample.mp3 --body /temp/media/sample.mp3 --content-type "audio/mpeg"
# echo "### COPY MP3 to my s3 bucket -- END ###"
# rm -rf /temp