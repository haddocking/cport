"""Error modules."""


class Error(Exception):
    """Base class for other exceptions."""


class IncompleteInputError(Error):
    """Raised when input is incomplete for a given predictor."""

    def __init__(self, predictor_name, missing=None):
        self.predictor_name = predictor_name
        self.message = "Incomplete input for"
        self.missing = missing
        super().__init__(self.message)

    def __str__(self):
        if self.missing:
            return (
                f"{self.message} {self.predictor_name} predictor, "
                f"missing: {self.missing}"
            )

        return f"{self.message} {self.predictor_name}"
