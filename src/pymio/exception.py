class MioTypeUnexpectedError(Exception):
    def __init__(self, expected_type, actual_type):
        super().__init__(f"Expected type: {expected_type}, but got: {actual_type}")
