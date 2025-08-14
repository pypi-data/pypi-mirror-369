class IncompleteResponseError(Exception):
    def __init__(self, message="Failed to fetch complete response. Please try again later.", status_code=503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)