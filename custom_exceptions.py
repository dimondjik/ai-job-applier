from dataclasses import dataclass
from utils import PrettyPrintable


# Here packed info that could be useful, filled when available
@dataclass
class CustomExceptionData(PrettyPrintable):
    reason: str = ""

    page_url: str = ""

    job_title: str = ""
    job_link: str = ""

    llm_question: str = ""
    llm_answer: str = ""


class BrowserClientException(Exception):
    def __init__(self, message: str, data: CustomExceptionData):
        super().__init__(message)
        self.data = data


class BotClientException(Exception):
    def __init__(self, message: str, data: CustomExceptionData):
        super().__init__(message)
        self.data = data


class LLMException(Exception):
    def __init__(self, message: str, data: CustomExceptionData):
        super().__init__(message)
        self.data = data
