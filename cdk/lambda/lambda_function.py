import json
import logging
from typing import Any, Dict

import boto3
from extras.exception import BaseError, S3ClientError, ValidationError
from extras.extractors import (NATURAL_LANGUAGE_PROCESSING_PIPELINE,
                               SimpleRegexInsightExtractor,
                               SpacyNLPInsightExtractor)
from extras.handlers import handle_transcription_job
from extras.response import ResponseAWS
from extras.validators import (check_s3_object_exists, sanitize_s3_uri,
                               sanitize_trackers, validate_input)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")


def lambda_handler(event: Dict[str, Any], context: Any) -> ResponseAWS:
    """
    AWS Lambda function handler to process audio file transcription requests.

    This function performs the following actions:
    1. Parses the incoming JSON request body to extract `interaction_url` and `trackers`.
    2. Validates the URL format and checks the existence and content type
       of the specified S3 object.
    3. Checks the status of a transcription job and returns insights if completed,
       or starts a new job if necessary.

    Args:
        event (Dict[str, Any]): The event dictionary passed by AWS Lambda
                                containing request details.
        context (Any): The context object provided by AWS Lambda with
                       runtime information.

    Returns:
        Dict[str, Any]: A dictionary representing the HTTP response, including:
            - statusCode (int): The HTTP status code.
            - body (str): The response body as a JSON string. Contains error messages
              or transcription insights.

    Headers:
        - The `X-Spacy` header can be used to specify whether to use Spacy for tracker extraction.
    """
    spacy_enabled = event["headers"].get("X-Spacy", None) == "True"

    try:
        body = json.loads(event["body"])
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON format: {str(e)}"
        logger.error(msg)
        return ResponseAWS(400, {"error": msg}).create_response()

    try:
        required_parameters = ("interaction_url", "trackers")
        validation_result = validate_input(body, required_parameters)

        interaction_url, trackers = (
            validation_result["interaction_url"],
            validation_result["trackers"],
        )

        trackers = sanitize_trackers(trackers)
        bucket_name, key = sanitize_s3_uri(interaction_url)

        check_s3_object_exists(bucket_name=bucket_name, key=key, s3_client=s3)

        extractor = (
            SimpleRegexInsightExtractor()
            if not spacy_enabled
            else SpacyNLPInsightExtractor(NATURAL_LANGUAGE_PROCESSING_PIPELINE)
        )

        return handle_transcription_job(
            interaction_url,
            bucket_name,
            key,
            trackers,
            s3_client=s3,
            transcribe_client=transcribe,
            extractor=extractor,
        )
    except (ValidationError, S3ClientError, BaseError) as e:
        logger.error(f"An error occurred: {e}")
        return ResponseAWS(400, {"error": e.get_error_message()}).create_response()
