from dataclasses import dataclass


@dataclass
class Filters:
    experience_level: list[str] = None
    industry: list[str] = None
    date: str = ""
    remote: list[str] = None
    job_type: list[str] = None
    location: list[str] = None
    title: list[str] = None

    @staticmethod
    def from_filters_yaml(filters_yaml):
        filters = Filters()

        filters.experience_level = [k for k, v in filters_yaml["experience_level"].items() if v]
        filters.industry = [k for k, v in filters_yaml["industry"].items() if v]
        filters.date = next((k for k, v in filters_yaml["date"].items() if v), "day")
        filters.remote = [k for k, v in filters_yaml["remote"].items() if v]
        filters.job_type = [k for k, v in filters_yaml["job_type"].items() if v]

        filters.location = filters_yaml["location"]
        filters.title = filters_yaml["title"]

        return filters
