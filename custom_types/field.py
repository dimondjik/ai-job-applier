from dataclasses import dataclass
from enum import Enum
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class Field:
    type: "FieldTypeEnum" = ""
    label: str = ""
    data: list[str] = None
    element: WebElement = None


class FieldTypeEnum(Enum):
    INPUT = 1
    LIST = 2
    UPLOAD = 3
    RADIO = 4
