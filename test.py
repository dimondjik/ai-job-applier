from llm_client import LLMClient
from config_manager import ConfigManager

if __name__ == "__main__":
    # llm = LLMClient()
    # print(llm.answer_freely("How many years of work experience do you have with C++?"))

    config = ConfigManager()

    print(config.linkedin_xpaths.easy_apply_element_radio_find.format(value="abc"))

    # g = (o for o in range(20))

    # for i in range(34):
    #     print(g.__next__())
