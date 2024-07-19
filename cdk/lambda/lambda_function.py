import json
import boto3
import os
import re
import time
import requests
import logging
from botocore.exceptions import ClientError
from urllib.parse import urlparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON format: {str(e)}"
        logger.error(msg)
        return {
            'statusCode': 400,
            'body': json.dumps({"error":msg})
        }
        
    interaction_url = body.get('interaction_url')
    trackers = body.get('trackers')
    
    if not interaction_url or not trackers:
        msg = f"Invalid JSON format, Not missing: 'interaction_url':{bool(interaction_url)}, 'trackers':{bool(trackers)}"
        logger.error(msg)
        return {
            'statusCode': 400,
            'body': json.dumps({"error":msg})
        }
    
    logger.info("Extracting bucket name and key")

    # "s3://mini-sedric-bucket-data-s3-all-mp3-media-0001/sample.mp3"
    # "s3.us-east-1.localhost.localstack.cloud:4566/mini-sedric-bucket-data-s3-all-mp3-media-0001/sample.mp3"
    parts = interaction_url.split('/')
    bucket_name = parts[-2]
    key = parts[-1]
    if not interaction_url.startswith('s3://') or not interaction_url.endswith('.mp3') or not bucket_name or not key:
        msg = "Invalid S3 URL format, expected:'s3://<bucket_name>/<file_name>.mp3'"
        logger.error(msg)
        return {
            'statusCode': 400,
            'body': json.dumps({"error": msg, "expected":"s3://<bucket_name>/<file_name>.mp3"})
        }
    

    logger.info("Validating Data")
    
    try:
        response = s3.head_object(Bucket=bucket_name, Key=key)
        content_type = response['ContentType']
        if content_type not in set({'audio/mpeg', 'audio/mp3'}):
            msg = "The file is not an mp3, The content types does not match 'audio/mpeg', 'audio/mp3'. Was the file uploaded with a correct Content Type?"
            logger.error(response)
            logger.error(content_type)
            logger.error(msg)
            return {
                'statusCode': 400,
                'body': json.dumps({"error": msg, "requested_file": interaction_url})
            }
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            msg = f"The specified object does not exist {key}"
            logger.error(msg)
            logger.error(e.response['Error']['Code'])
            return {
                'statusCode': 404,
                'body': json.dumps({"error": msg, "requested_url": interaction_url})
            }
        else:
            raise e
    
    
    job_name = f"transcriptionJob-{bucket_name.replace('/', '-')}-{key.replace('/', '-')}"
    try:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status == 'COMPLETED':
            logger.info("Transcription job completed")
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            try:
                logger.info("Transcription COMPLETED")
                transcript_key = job_name+'.json'
                response = s3.get_object(Bucket=bucket_name, Key=transcript_key)
                transcript_data = response['Body'].read().decode('utf-8')
                transcript_json = json.loads(transcript_data)
                logger.info("Extracting insignts COMPLETED")
                
                transcript_text = transcript_json['results']['transcripts'][0]['transcript']
                insights = []
                sentences = transcript_text.split('.')
                for i, sentence in enumerate(sentences):
                    for tracker in trackers:
                        # only first occurance
                        matched = re.search(rf'\b{tracker}\b', sentence)
                        if matched:
                            insights.append({
                                'sentence_index': i,
                                'start_word_index': len(sentence[:matched.start()].split()),
                                'end_word_index': len(sentence[:matched.end()].split()),
                                'tracker_value': tracker,
                                'transcribe_value': sentence.strip()
                            })

                return {
                    'statusCode': 200,
                    'body': json.dumps({'insights': insights})
                }
                
                # return {
                #     'statusCode': 200,
                #     'body': json.dumps({"status": job_status, "transcript_uri": transcript_uri, "transcript_json": transcript_json})
                # }
            except s3.exceptions.NoSuchKey:
                logger.error(f"The specified key does not exist in the bucket: {transcript_key}")
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Transcription result not found'})
                }
   
        elif job_status == 'FAILED':
            msg = "Transcription job failed"
            logger.error(msg)
            return {
                'statusCode': 400,
                'body': json.dumps({"status": job_status})
            }
        else:
            msg = "Job still pending"
            logger.info(msg)
            return {
                'statusCode': 202,
                'body': json.dumps({"status": job_status})
            }
    except transcribe.exceptions.NotFoundException:
        logger.info(f"Starting new transcription job: {job_name}")
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': interaction_url},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )
        return {
            'statusCode': 202,
            'body': json.dumps({"message": "Transcription job started", "job_name": job_name})
        }
