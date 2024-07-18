import json
import boto3
import os
import re
import time
import requests


s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")


def lambda_handler(event, context):
    body = json.load(event['body'])
    interaction_url = body['interaction_url']
    trackers = body['trackers']
    
    if not interaction_url or not trackers:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing data for transcritpion")
        }
        
    bucket_name = interaction_url.split('/')[2]
    key = '/'.join(interaction_url.split('/')[3:])
    
    job_name = "transcriptionJob"
    transcribe.start_transcription_job(
        TranscriptionJobName = job_name,
        Media = {'MediaFileUri': interaction_url},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName = job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)
        
    if status["TranscriptionJob"]["TranscriptionJobStatus"] == 'FAILED':
        return {
            'statusCode': 500,
            'body': json.dumps('Transcription failed')
        }
        
    transcription_url =  status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    transcription_response = requests.get(transcription_url)
    transcription_result = transcription_response.json()
    transcript = transcription_result['results']['transcripts'][0]['transcript']
    
    
    insights = []
    sentences = transcript.split('.')
    for i, sentence in enumerate(sentences):
        for tracker in trackers:
            # only first occurance
            match = re.search(rf'\b{tracker}\b')
            if match:
                insights.append({
                    'sentence_index': i,
                    'start_word_index': len(sentence[:match.start()].split()),
                    'end_word_index': len(sentence[:match.end()].split()),
                    'tracker_value': tracker,
                    'transcribe_value': sentence.strip()
                })
                
    return {
        'statusCode': 200,
        'body': json.dumps({'insights': insights})
    }
