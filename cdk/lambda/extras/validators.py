from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")


def validate_input(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the input JSON body for required fields.

    Args:
        body (Dict[str, Any]): The JSON body of the request.

    Returns:
        Dict[str, Any]: A dictionary with the validation status and error message if any.
    """
    interaction_url = body.get("interaction_url")
    trackers = body.get("trackers")

    if not interaction_url or not trackers:
        return {"error": "Invalid JSON format, missing 'interaction_url' or 'trackers'"}

    return {"interaction_url": interaction_url, "trackers": trackers}