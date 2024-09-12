from dataclasses import dataclass


@dataclass
class Job:
    title: str = ""
    company: str = ""
    location: str = ""
    desc: str = ""
    hr: str = ""
    link: str = ""
    applied: bool = True
