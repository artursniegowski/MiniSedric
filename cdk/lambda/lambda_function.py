import logging
from typing import Any, Dict

import boto3
from extras.exception import (BaseError, S3ClientError, TranscriptionJobError,
                              ValidationError)
from extras.extractors import (NATURAL_LANGUAGE_PROCESSING_PIPELINE,
                               SimpleRegexInsightExtractor,
                               SpacyNLPInsightExtractor)
from extras.handlers import (handle_insights_extraction,
                             handle_transcription_job)
from extras.response import ResponseAWS
from extras.validators import (parse_body, parse_s3_uri, validate_input,
                               validate_trackers)

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

        body = parse_body(event)

        required_parameters = ("interaction_url", "trackers")
        validation_result = validate_input(body, required_parameters)

        interaction_url, trackers = (
            validation_result["interaction_url"],
            validation_result["trackers"],
        )

        trackers = validate_trackers(trackers)
        bucket_name, key = parse_s3_uri(interaction_url)

        transcription_status, transcription_text = handle_transcription_job(
            bucket_name,
            key,
            s3_client=s3,
            transcribe_client=transcribe,
        )

        if transcription_status != "COMPLETED":
            return ResponseAWS(202, {"transcription status": transcription_status}).create_response()

        extractor = (
            SimpleRegexInsightExtractor()
            if not spacy_enabled
            else SpacyNLPInsightExtractor(NATURAL_LANGUAGE_PROCESSING_PIPELINE)
        )
        insights = handle_insights_extraction(
            transcription_text, trackers, extractor=extractor
        )

        return ResponseAWS(200, {"insights": insights}).create_response()

    except (ValidationError, S3ClientError, BaseError, TranscriptionJobError) as e:
        logger.error(f"An error occurred: {e}")
        return ResponseAWS(400, {"error": e.get_error_message()}).create_response()
