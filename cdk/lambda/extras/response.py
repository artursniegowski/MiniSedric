import json
from typing import Any, Dict


class ResponseAWS:
    """
    Creates and formats HTTP responses for AWS Lambda functions.
    """

    def __init__(self, status_code: int, body: Dict[str, Any]):
        self.status_code = status_code
        self.body = body

    def create_response(self) -> Dict[str, Any]:
        return {"statusCode": self.status_code, "body": json.dumps(self.body)}
