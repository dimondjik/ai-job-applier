import yaml
import os
from utils import Singleton
from custom_types import *


# Making this a singleton class
class ConfigManager(metaclass=Singleton):
    def __init__(self):
        # TODO: Should I pack this in dataclass?
        self.linkedin_pass: str = ""
        self.linkedin_email: str = ""
        self.openai_api_key: str = ""
        self.deepseek_api_key: str = ""

        self.blacklist: Blacklist

        self.filters: Filters

        self.prompt_answer_with_options: FewShotPrompt
        self.prompt_answer_freely: FewShotPrompt

        self.user_info: UserInfo

        self.linkedin_xpaths: LinkedinXPaths

        self.__load_config()

    def __reload_blacklist(self):
        with open(os.path.join(os.getcwd(), "app_config", "blacklist.yaml"), "r", encoding="UTF-8") as f:
            blacklist_yaml = yaml.safe_load(f)
            self.blacklist = Blacklist.from_blacklist_yaml(blacklist_yaml)

    def __load_config(self):
        with open(os.path.join(os.getcwd(), "app_config", "secrets.yaml"), "r", encoding="UTF-8") as f:
            secrets_yaml = yaml.safe_load(f)
            self.linkedin_pass = secrets_yaml["password"]
            self.linkedin_email = secrets_yaml["email"]
            self.openai_api_key = secrets_yaml["openai_api_key"]
            self.deepseek_api_key = secrets_yaml["deepseek_api_key"]

        with open(os.path.join(os.getcwd(), "app_config", "filters.yaml"), "r", encoding="UTF-8") as f:
            filters_yaml = yaml.safe_load(f)
            self.filters = Filters.from_filters_yaml(filters_yaml)

        with open(os.path.join(os.getcwd(), "app_config", "prompts.yaml"), "r", encoding="UTF-8") as f:
            prompts_yaml = yaml.safe_load(f)
            self.prompt_answer_with_options = FewShotPrompt.from_prompts_yaml(prompts_yaml["answer_with_options"])
            self.prompt_answer_freely = FewShotPrompt.from_prompts_yaml(prompts_yaml["answer_freely"])

        with open(os.path.join(os.getcwd(), "app_config", "user_info.yaml"), "r", encoding="UTF-8") as f:
            user_info_yaml = yaml.safe_load(f)
            self.user_info = UserInfo.from_user_info_yaml(user_info_yaml)

        with open(os.path.join(os.getcwd(), "app_config", "xpaths.yaml"), "r", encoding="UTF-8") as f:
            xpaths_yaml = yaml.safe_load(f)
            self.linkedin_xpaths = LinkedinXPaths.from_linkedin_xpaths_yaml(xpaths_yaml["linkedin"])

    def __getattribute__(self, name):
        # Reload blacklist configs on the fly, every time they are accessed
        # I have a feeling that could be done cleaner, but should work for now :)
        if any([name in n for n in ["blacklist_mode", "company", "title_keywords"]]):
            self.__reload_blacklist()
        # Default __getattribute__ behaviour
        return object.__getattribute__(self, name)
