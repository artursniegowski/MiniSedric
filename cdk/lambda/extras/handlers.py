import json
import logging

from extras.exception import BaseError, S3ClientError
from extras.extractors import InsightExtractor
from extras.response import ResponseAWS
from extras.types import S3ClientType, TranscribeClientType
from extras.validators import check_s3_object_exists

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle_transcript_text_from_s3_job(
    bucket_name: str,
    transcript_key: str,
    s3_client: S3ClientType,
) -> str:
    """
    Retrieve the transcript text from an S3 object.

    Args:
        bucket_name (str): The name of the S3 bucket.
        transcript_key (str): The key of the S3 object.
        s3_client (S3ClientType): client to interact with s3 bucket

    Returns:
        str: The transcript text
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=transcript_key)
        data = response["Body"].read().decode("utf-8")
        transcript_json = json.loads(data)
        return transcript_json["results"]["transcripts"][0]["transcript"]
    except s3_client.exceptions.NoSuchKey:
        raise S3ClientError(
            {
                "error": {
                    "error_message": "The specified key does not exist in the bucket",
                    "error": f"Error retrieving {bucket_name} {transcript_key}",
                }
            }
        )
    except KeyError:
        raise BaseError(
            {
                "error": {
                    "error_message": "Missing key in the response or data dictionary",
                    "error": f"Error retrieving {bucket_name} {transcript_key}",
                }
            }
        )


def handle_transcription_job(
    bucket_name: str,
    key: str,
    trackers: list[str],
    s3_client: S3ClientType,
    transcribe_client: TranscribeClientType,
    extractor: InsightExtractor,
) -> ResponseAWS:
    """
    Handle the transcription job of the audio file.

    Args:
        bucket_name (str): The name of the S3 bucket.
        key (str): The key of the S3 object.
        trackers (list): The list of trackers to extract insights.
        s3_client (S3ClientType): client to interact with s3 bucket
        transcribe_client (TranscribeClientType): client for transcribe service
        extractor (InsightExtractor): The strategy for extracting insights.

    Returns:
        Dict[int, str]: The response with the satatus
    """
    check_s3_object_exists(bucket_name=bucket_name, key=key, s3_client=s3_client)

    job_name = f"transcriptionJob-{bucket_name}-{key.replace('/', '-')}"
    try:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
        if job_status == "COMPLETED":
            logger.info(f"Transcription job: {job_name} completed.")

            transcript_key = job_name + ".json"
            transcript_result = handle_transcript_text_from_s3_job(
                bucket_name, transcript_key, s3_client=s3_client
            )

            insights = extractor.extract_insights(transcript_result, trackers)

            return ResponseAWS(
                200, {"status": "COMPLETED", "insights": insights}
            ).create_response()

        elif job_status == "FAILED":
            msg = "Transcription job failed"
            logger.error(msg)
            return ResponseAWS(400, {"status": job_status}).create_response()
        else:
            msg = "Job still pending"
            logger.info(msg)
            return ResponseAWS(202, {"status": job_status}).create_response()

    except transcribe_client.exceptions.NotFoundException:
        logger.info(f"Starting new transcription job: {job_name}")
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": f"s3://{bucket_name}/{key}"},
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
