class ValidationError(Exception):
    def __init__(self, message):
        if not isinstance(message, dict) or "error" not in message:
            raise ValueError(
                "ValidationError must be initialized with a dictionary containing an 'error' key."
            )
        super().__init__(message)
