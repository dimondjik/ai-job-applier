from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from config_manager import ConfigManager
from langchain_core.messages import AIMessage
import logging

logger = logging.getLogger("LLMClient")


class ChatOpenAIWrapper:
    def __init__(self):
        """
        Langchain's ChatOpenAI class with some additional functionality  
        
        """  # noqa

        self.config = ConfigManager()
        self.llm_chat = ChatOpenAI(model="gpt-4o-2024-08-06",
                                   openai_api_key=self.config.openai_api_key,
                                   temperature=0.42)

    def invoke(self, messages):
        logger.info("Calling OpenAI")
        return self.llm_chat.invoke(messages)

    def __call__(self, messages):
        return self.invoke(messages)


class LLMClient:
    def __init__(self):
        self.llm_chat = ChatOpenAIWrapper()
        self.config = ConfigManager()
        self.keyword = "CANDIDATE_ANSWER: "
    # jobs-easy-apply-repeatable-groupings__groupings
    @staticmethod
    def __build_prompt(config_manager_prompt, force_single_shot=True) -> ChatPromptTemplate:
        example_prompt = ChatPromptTemplate.from_messages([
            ("user", "{input}"),
            ("ai", "{output}")
        ])

        if force_single_shot:
            examples = [{"input": config_manager_prompt.examples[0].user_message,
                         "output": config_manager_prompt.examples[0].ai_message}]
        else:
            examples = [{"input": ex.user_message, "output": ex.ai_message} for ex in config_manager_prompt.examples]

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", config_manager_prompt.system_message),
            few_shot_prompt,
            ("human", config_manager_prompt.user_message_template)
        ])

        return prompt

    def __keyword_parser(self, message: AIMessage) -> str:
        message_string = message.content

        logger.debug(f"Full LLM answer: \n {message_string}")

        keyword_index = message_string.rfind(self.keyword)
        if keyword_index == -1:
            return ""
        else:
            return message_string[keyword_index + len(self.keyword):]

    def answer_freely(self, question: str) -> tuple[bool, str]:
        """
        Answer on question in free format

        Boolean shows if LLM was able to answer a question

        :param question: Question about resume to answer

        :return: Call result and answer
        """
        prompt = self.__build_prompt(self.config.prompt_answer_freely)

        logger.debug("Full LLM prompt: \n {}".format(
            prompt.invoke({"resume": str(self.config.user_info),
                           "question": question})))

        chain = prompt | self.llm_chat | self.__keyword_parser

        with get_openai_callback() as cb:
            answer = chain.invoke({"resume": str(self.config.user_info),
                                   "question": question})
            logger.warning(f"OpenAI CALLBACK:\n {cb}")

        if answer:
            logger.info(f"LLM answer:\n {answer}")
            return True, answer
        else:
            logger.info(f"LLM did not produce {self.keyword}!")
            return False, answer

    def answer_with_options(self, question: str, options: list[str]) -> tuple[bool, str]:
        """
        Answer on question from options provided

        Boolean shows if LLM was able to answer a question

        :param question: Question about resume to answer
        :param options: Options to choose from

        :return: Call result and answer
        """
        prompt = self.__build_prompt(self.config.prompt_answer_with_options)

        logger.debug("Full LLM prompt: \n {}".format(
            prompt.invoke({"resume": str(self.config.user_info),
                           "question": question,
                           "options": str(options)})))

        chain = prompt | self.llm_chat | self.__keyword_parser

        with get_openai_callback() as cb:
            answer = chain.invoke({"resume": str(self.config.user_info),
                                   "question": question,
                                   "options": str(options)})
            logger.warning(f"OpenAI CALLBACK:\n {cb}")

        if answer:
            logger.info(f"LLM answer:\n {answer}")
            return True, answer
        else:
            logger.info(f"LLM did not produce {self.keyword}!")
            return False, answer
