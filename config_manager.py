import yaml
import os
from utils import Singleton


# Making this a singleton class
class ConfigManager(metaclass=Singleton):
    def __init__(self):
        self.linkedin_pass = ""
        self.linkedin_email = ""
        self.openai_api_key = ""

        self.easy_apply = True
        self.experience_level = []
        self.industry = []
        self.date = ""
        self.remote = []
        self.job_type = []
        self.location = ""
        self.title = ""

        self.blacklist_mode = []
        self.blacklist_company = []
        self.blacklist_keywords = []

        self.__load_config()

    def __load_config(self):
        with open(os.path.join(os.getcwd(), "app_config", "secrets.yaml"), "r", encoding="UTF-8") as f:
            secrets_yaml = yaml.safe_load(f)
            self.linkedin_pass = secrets_yaml["password"]
            self.linkedin_email = secrets_yaml["email"]
            self.openai_api_key = secrets_yaml["openai_api_key"]

        with open(os.path.join(os.getcwd(), "app_config", "filters.yaml"), "r", encoding="UTF-8") as f:
            filters_yaml = yaml.safe_load(f)
            self.experience_level = filters_yaml["experience_level"]
            self.industry = filters_yaml["industry"]
            self.date = filters_yaml["date"]
            self.remote = filters_yaml["remote"]
            self.job_type = filters_yaml["job_type"]
            self.location = filters_yaml["location"]
            self.title = filters_yaml["title"]

        with open(os.path.join(os.getcwd(), "app_config", "blacklist.yaml"), "r", encoding="UTF-8") as f:
            blacklist_yaml = yaml.safe_load(f)
            self.blacklist_company = blacklist_yaml["company"]
            self.blacklist_title_keywords = blacklist_yaml["title_keywords"]

    def __getattribute__(self, name):
        # Reload configs on the fly, every time they are accessed
        # I have a feeling that could be done much cleaner, but should work for now :)
        if name in ["experience_level",
                    "industry",
                    "date",
                    "remote",
                    "job_type",
                    "location",
                    "title",
                    "blacklist_mode",
                    "blacklist_company",
                    "blacklist_keywords"]:
            self.__load_config()
        # Default __getattribute__ behaviour
        return object.__getattribute__(self, name)
