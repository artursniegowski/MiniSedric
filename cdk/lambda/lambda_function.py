import json
import logging
from typing import Any, Dict

from extras.extractors import (NATURAL_LANGUAGE_PROCESSING_PIPELINE,
                               SimpleRegexInsightExtractor,
                               SpacyNLPInsightExtractor)
from extras.handlers import handle_transcription_job
from extras.response import ResponseAWS
from extras.validators import (check_s3_object_exists, sanitize_s3_uri,
                               sanitize_trackers, validate_input)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    required_parameters = ("interaction_url", "trackers")

    validation_result = validate_input(body, required_parameters)
    if "error" in validation_result:
        msg = f"Invalid JSON format: {validation_result["error"]}"
        logger.error(msg)
        return ResponseAWS(400, {"error": validation_result["error"]}).create_response()

    interaction_url = validation_result["interaction_url"]
    trackers = validation_result["trackers"]

    sanitized_tackers = sanitize_trackers(trackers)
    if "error" in sanitized_tackers:
        msg = f"Invalid trackers format: {sanitized_tackers["error"]}"
        logger.error(msg)
        return ResponseAWS(400, {"error": sanitized_tackers["error"]}).create_response()
    trackers = sanitized_tackers["trackers"]

    sanitized_s3_uri = sanitize_s3_uri(interaction_url)
    if "error" in sanitized_s3_uri:
        msg = f"Invalid S3 URI format: {sanitized_s3_uri["error"]}"
        logger.error(msg)
        return ResponseAWS(400, {"error": sanitized_s3_uri["error"]}).create_response()

    bucket_name, key = sanitized_s3_uri["bucket_name"], sanitized_s3_uri["key"]

    s3_object_exists = check_s3_object_exists(bucket_name=bucket_name, key=key)
    if "error" in s3_object_exists:
        msg = f"S3 object does NOT exists: {s3_object_exists["error"]}"
        logger.error(msg)
        return ResponseAWS(400, {"error": s3_object_exists["error"]}).create_response()

    return handle_transcription_job(
        interaction_url,
        bucket_name,
        key,
        trackers,
        extractor=(
            SimpleRegexInsightExtractor()
            if not spacy_enabled
            else SpacyNLPInsightExtractor(NATURAL_LANGUAGE_PROCESSING_PIPELINE)
        ),
        # extractor=SimpleRegexInsightExtractor(),
        # extractor=SpacyNLPInsightExtractor(NATURAL_LANGUAGE_PROCESSING_PIPELINE),
    )
