import json
import re
from typing import Any, Dict, Tuple

from botocore.exceptions import ClientError
from extras.exception import S3ClientError, ValidationError
from extras.types import S3ClientType


def validate_input(body: Dict[str, Any], required_fields: Tuple[str]) -> Dict[str, Any]:
    """
    Validate the input JSON body for required fields.

    Args:
        body (Dict[str, Any]): The JSON body of the request.
        required_fields (Tuple[str]): Required fields to validate.

    Returns:
        Dict[str, Any]: A dictionary with either validation errors or the validated data.
                        - If there are errors, the dictionary will contain an 'error' key with details.
                        - If validation is successful, the dictionary will contain the validated data.
    """
    if not required_fields:
        raise ValidationError({"error": "required_fields is empty"})
    else:
        required_fields = tuple(set(required_fields))

    data, errors = {}, {}
    for field in required_fields:
        if current_field := body.get(field):
            data[field] = current_field
        else:
            errors[field] = "Missing or empty field"

    if errors:
        raise ValidationError(
            {"error": {"error": errors, "error_message": "Invalid JSON format"}}
        )

    return data


def _is_valid_bucket_name(bucket_name: str) -> bool:
    """
    Validate the bucket name against AWS S3 bucket naming rules.

    Args:
        bucket_name (str): The bucket name to validate.

    Returns:
        bool: True if the bucket name is valid, otherwise False.
    """
    # Length check
    if not (3 <= len(bucket_name) <= 63):
        return False

    # Characters check
    if not re.match(r"^[a-z0-9.-]+$", bucket_name):
        return False

    # Start and end check
    if not (bucket_name[0].isalnum() and bucket_name[-1].isalnum()):
        return False

    # No adjacent periods
    if ".." in bucket_name:
        return False

    # Not formatted as an IP address
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", bucket_name):
        return False

    # Reserved prefixes and suffixes
    if bucket_name.startswith(("xn--", "sthree-", "sthree-configurator")):
        return False
    if bucket_name.endswith(("-s3alias", "--ol-s3")):
        return False

    return True


def parse_s3_uri(interaction_url: str) -> tuple[str, str]:
    """
    validate the S3 URI and extract the bucket name and key.

    This function performs the following:
    1. Validates that the URI starts with "s3://" and ends with ".mp3".
    2. Extracts the bucket name and key from the URI.

    Args:
        interaction_url (str): The S3 URI to be sanitized and validated.

    Returns:
        tuple[str, str]: A tuple with  extracted bucket name and key.
            - If the URI is invalid, the dictionary will contain an 'error' key with details.
            - If the URI is valid, the dictionary will contain 'bucket_name' and 'key'.
    """
    EXPECTED_S3_URI = "s3://<bucket_name>/<file_name>.mp3"

    pattern = r"^s3://(?P<bucket_name>[^/]+)/(?P<key>.+\.mp3)$"
    match = re.match(pattern, interaction_url)

    if match:
        bucket_name = match.group("bucket_name")
        key = match.group("key")
        if _is_valid_bucket_name(bucket_name=bucket_name):
            return bucket_name, key
        else:
            raise ValidationError(
                {
                    "error": {
                        "error": f"Invalid S3 bucket name {bucket_name} - refer to AWS bucket name rules.",
                        "expected": EXPECTED_S3_URI,
                    }
                }
            )
    else:
        raise ValidationError(
            {
                "error": {
                    "error": f"Invalid S3 URI format {interaction_url}",
                    "expected": EXPECTED_S3_URI,
                }
            }
        )


def validate_trackers(trackers: Any) -> list[str]:
    """
    Validate the trackers input to ensure it is a list of strings.

    Args:
        trackers (Any): The input to validate.

    Returns:
       list[str]: A list with the validated trackers .
    """
    if not isinstance(trackers, list):
        raise ValidationError(
            {
                "error": {
                    "error": "Trackers must be a list",
                    "error_message": "Invalid trackers format",
                }
            }
        )

    if not all(isinstance(tracker, str) for tracker in trackers):
        raise ValidationError(
            {
                "error": {
                    "error": "All trackers must be strings",
                    "error_message": "Invalid trackers format",
                }
            }
        )

    non_empty_trackers = [tracker for tracker in trackers if tracker.strip()]
    if len(non_empty_trackers) != len(trackers):
        raise ValidationError(
            {
                "error": {
                    "error": "Trackers cannot be empty strings",
                    "error_message": "Invalid trackers format",
                }
            }
        )

    return trackers


def check_s3_object_exists(
    bucket_name: str,
    key: str,
    s3_client: S3ClientType,
    with_content_type_check: bool = True,
) -> bool:
    """
    Check if the S3 object exists and is of the correct type.

    Args:
        bucket_name (str): The name of the S3 bucket.
        key (str): The key of the S3 object.
        with_content_type_check (bool): Weather to use content type check
                                        to validate the object
        s3_client (S3ClientType): boto client to interact with s3 bucket
    Returns:
        bool: Indicating the existance status
    """
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=key)
        content_type = response["ContentType"]
        if with_content_type_check and content_type not in {"audio/mpeg", "audio/mp3"}:
            raise ValidationError(
                {
                    "error": f"The file {bucket_name} {key} is not an mp3 or the content type is incorrect"
                }
            )
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            raise S3ClientError(
                {"error": f"The specified object does not exist: {bucket_name} {key}"}
            )
        else:
            raise S3ClientError(
                {
                    "error": {
                        "error": str(e),
                        "error_message": f"Cant retrive the object: {key}",
                    }
                }
            )

    return True


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(event["body"])
    except json.JSONDecodeError as e:
        raise ValidationError({"error": f"Invalid JSON format: {str(e)}"})
