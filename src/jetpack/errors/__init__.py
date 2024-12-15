class GenericErrors(Exception):
    """Generic Error"""

    def __init__(
        self,
        message: str = "An error has occurred. Please contact support.",
        ec: str | None = None,
        status_code: int = 500,
    ):
        self._ec = ec
        self._message = f"{ec}: {message}" if ec else message
        self._status_code = status_code
        super().__init__(self.message)

    @property
    def status_code(self):
        return self._status_code

    @property
    def message(self):
        return self._message

    @property
    def ec(self):
        return self._ec

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @message.setter
    def message(self, value):
        self._message = value

    @ec.setter
    def ec(self, value):
        self._ec = value
