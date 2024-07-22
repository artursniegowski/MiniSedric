import json
import logging
from typing import Any, Dict

import boto3
from extras.extractors import InsightExtractor
from extras.response import ResponseAWS

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle_transcript_text_from_s3_job(
    bucket_name: str, transcript_key: str
) -> Dict[str, Any]:
    """
    Retrieve the transcript text from an S3 object and handle any errors.

    Args:
        bucket_name (str): The name of the S3 bucket.
        transcript_key (str): The key of the S3 object.

    Returns:
        Dict[str, Any]: The transcript text or an error message.
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=transcript_key)
        data = response["Body"].read().decode("utf-8")
        transcript_json = json.loads(data)
        transcript_text = transcript_json["results"]["transcripts"][0]["transcript"]
        return {"transcript_text": transcript_text}
    except s3.exceptions.NoSuchKey:
        return {"error": "The specified key does not exist in the bucket"}
    except KeyError:
        return {"error": "Key is missing in the response or data dictionary."}


def handle_transcription_job(
    interaction_url: str,
    bucket_name: str,
    key: str,
    trackers: list[str],
    extractor: InsightExtractor,
) -> ResponseAWS:
    """
    Handle the transcription job by checking its status and processing the result.

    Args:
        interaction_url (str): The URL of the interaction to be transcribed.
        bucket_name (str): The name of the S3 bucket.
        key (str): The key of the S3 object.
        trackers (list): The list of trackers to extract insights.
        extractor (InsightExtractor): The strategy for extracting insights.

    Returns:
        Dict[str, Any]: A dictionary representing the HTTP response.
    """
    job_name = f"transcriptionJob-{bucket_name}-{key.replace('/', '-')}"
    try:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
        if job_status == "COMPLETED":
            logger.info(f"Transcription job: {job_name} completed.")

            transcript_key = job_name + ".json"
            transcript_result = handle_transcript_text_from_s3_job(
                bucket_name, transcript_key
            )
            if "error" in transcript_result:
                msg = (
                    f"Error retrieving transcript from S3: {transcript_result['error']}"
                )
                logger.error(msg)
                return ResponseAWS(
                    400, {"error": transcript_result["error"]}
                ).create_response()

            transcript_text = transcript_result["transcript_text"]

            insights = extractor.extract_insights(transcript_text, trackers)
            return ResponseAWS(200, {"insights": insights}).create_response()

        elif job_status == "FAILED":
            msg = "Transcription job failed"
            logger.error(msg)
            return ResponseAWS(400, {"status": job_status}).create_response()
        else:
            msg = "Job still pending"
            logger.info(msg)
            return ResponseAWS(202, {"status": job_status}).create_response()

    except transcribe.exceptions.NotFoundException:
        logger.info(f"Starting new transcription job: {job_name}")
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": interaction_url},
            MediaFormat="mp3",
            LanguageCode="en-US",
        )
        return ResponseAWS(
            202,
            {
                "staus": "STARTED",
                "job_name": job_name,
            },
        ).create_response()
