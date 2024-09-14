from dataclasses import dataclass
from enum import Enum


class BlacklistEnum(Enum):
    WHOLE_WORDS = 0
    PARTIAL_WORDS = 1
    LLM_FILTER = 0


STR_TO_BLACKLIST_ENUM = {"whole_words": BlacklistEnum.WHOLE_WORDS,
                         "partial_words": BlacklistEnum.PARTIAL_WORDS,
                         "llm_filter": BlacklistEnum.LLM_FILTER}


@dataclass
class Blacklist:
    blacklist_mode: BlacklistEnum = None
    company: list[str] = None
    title_keywords: list[str] = None

    @staticmethod
    def from_blacklist_yaml(blacklist_yaml):
        blacklist = Blacklist()
        blacklist.blacklist_mode = next((STR_TO_BLACKLIST_ENUM[k]
                                         for k, v in blacklist_yaml["blacklist_mode"].items() if v))
        blacklist.company = blacklist_yaml["company"]
        blacklist.title_keywords = blacklist_yaml["title_keywords"]
        return blacklist
