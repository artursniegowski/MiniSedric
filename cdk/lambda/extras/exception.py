class BaseError(Exception):
    """Base class for all custom exceptions."""

    def __init__(self, message: dict):
        if not isinstance(message, dict) or "error" not in message:
            raise ValueError(
                "BaseError must be initialized with a dictionary containing an 'error' key."
            )
        super().__init__(message)
        self.message = message

    def get_error_message(self):
        return self.message.get("error", "Unknown error")


class ValidationError(BaseError):
    """Exception raised for validation errors."""

    pass


class S3ClientError(BaseError):
    """Exception raised for S3 client errors."""

    pass


class TranscribeClientError(BaseError):
    """Exception raised for transcribe client errors."""

    pass
