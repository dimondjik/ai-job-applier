from dataclasses import dataclass


@dataclass
class EasyApplyExceptionData:
    job_title: str = ""
    job_link: str = ""
    reason: str = ""


class LoginFailException(Exception):
    pass


class JobListException(Exception):
    pass


class EasyApplyException(Exception):
    def __init__(self, message: str, data: EasyApplyExceptionData):
        super().__init__(message)
        self.data = data
