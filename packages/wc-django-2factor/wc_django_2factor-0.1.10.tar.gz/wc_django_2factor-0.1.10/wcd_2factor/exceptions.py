class TwoFactorError(Exception):
    pass


class WrongBackend(TwoFactorError):
    backend_name: str

    def __init__(self, backend_name):
        self.backend_name = backend_name

    def __str__(self):
        return f'Incorrect 2factor backend: "{self.backend_name}".'


class MissingBackend(WrongBackend):
    def __str__(self):
        return f'No such backend exists: "{self.backend_name}".'
