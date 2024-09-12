import yaml
import os
from utils import Singleton
from custom_types.user_info import UserInfo
from custom_types.prompt import FewShotPrompt


# Making this a singleton class
class ConfigManager(metaclass=Singleton):
    def __init__(self):
        self.linkedin_pass: str = ""
        self.linkedin_email: str = ""
        self.openai_api_key: str = ""

        self.easy_apply: bool = True
        self.experience_level: dict[str, bool] = {}
        self.industry: dict[str, bool] = {}
        self.date: dict[str, bool] = {}
        self.remote: dict[str, bool] = {}
        self.job_type: dict[str, bool] = {}

        self.location: list[str] = []
        self.title: list[str] = []

        self.blacklist_mode: list[bool] = []
        self.blacklist_company: list[str] = []
        self.blacklist_keywords: list[str] = []

        self.prompt_answer_with_options: FewShotPrompt
        self.prompt_answer_freely: FewShotPrompt

        self.user_info: UserInfo

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

        with open(os.path.join(os.getcwd(), "app_config", "prompts.yaml"), "r", encoding="UTF-8") as f:
            prompts_yaml = yaml.safe_load(f)
            self.prompt_answer_with_options = FewShotPrompt.from_prompts_yaml(prompts_yaml["answer_with_options"])
            self.prompt_answer_freely = FewShotPrompt.from_prompts_yaml(prompts_yaml["answer_freely"])

        with open(os.path.join(os.getcwd(), "app_config", "user_info.yaml"), "r", encoding="UTF-8") as f:
            user_info_yaml = yaml.safe_load(f)
            self.user_info = UserInfo.from_user_info_yaml(user_info_yaml)

    def __getattribute__(self, name):
        # Reload configs on the fly, every time they are accessed
        # I have a feeling that could be done cleaner, but should work for now :)
        if name in ["blacklist_mode",
                    "blacklist_company",
                    "blacklist_keywords"]:
            self.__load_config()
        # Default __getattribute__ behaviour
        return object.__getattribute__(self, name)
