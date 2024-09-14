from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from config_manager import ConfigManager, FewShotPrompt
from langchain_core.messages import AIMessage
import logging
from html.parser import HTMLParser

logger = logging.getLogger("LLMClient")


class ChatOpenAIWrapper:
    def __init__(self):
        """
        Langchain's ChatOpenAI class with some additional functionality  
        """  # noqa

        self.config = ConfigManager()
        self.llm_chat = ChatOpenAI(model="gpt-4o-2024-08-06",
                                   openai_api_key=self.config.openai_api_key,
                                   temperature=0.32)

    def invoke(self, messages):
        logger.info("Calling OpenAI")
        return self.llm_chat.invoke(messages)

    def __call__(self, messages):
        return self.invoke(messages)


class LLMClient:
    def __init__(self):
        self.llm_chat = ChatOpenAIWrapper()
        self.config = ConfigManager()
        # self.keyword = "CANDIDATE_ANSWER:"
        self.no_answer_keyword = "CANDIDATE_NO_DATA"
        self.key_tag = "ANSWER"

    @staticmethod
    def __build_prompt(config_manager_prompt: FewShotPrompt, prompt_example_mode: int = 0) -> ChatPromptTemplate:
        """
        Build prompt, essentially getting from config
        
        :param config_manager_prompt: prompt object from config
        :param prompt_example_mode: 0 zer shot, 1 one shot, 2 few shots
        :return: langchain's ChatPromptTemplate
        """  # noqa

        example_prompt = ChatPromptTemplate.from_messages([
            ("user", "{input}"),
            ("ai", "{output}")
        ])

        match prompt_example_mode:
            case 0:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", config_manager_prompt.system_message),
                    ("human", config_manager_prompt.user_message_template)
                ])

            case 1:
                single_shot = [{"input": config_manager_prompt.examples[0].user_message,
                                "output": config_manager_prompt.examples[0].ai_message}]

                single_shot_prompt = FewShotChatMessagePromptTemplate(
                    example_prompt=example_prompt,
                    examples=single_shot
                )

                prompt = ChatPromptTemplate.from_messages([
                    ("system", config_manager_prompt.system_message),
                    single_shot_prompt,
                    ("human", config_manager_prompt.user_message_template)
                ])

            case 2:
                few_shot = [{"input": ex.user_message, "output": ex.ai_message} for ex in
                            config_manager_prompt.examples]

                few_shot_prompt = FewShotChatMessagePromptTemplate(
                    example_prompt=example_prompt,
                    examples=few_shot
                )

                prompt = ChatPromptTemplate.from_messages([
                    ("system", config_manager_prompt.system_message),
                    few_shot_prompt,
                    ("human", config_manager_prompt.user_message_template)
                ])

            case _:
                raise

        return prompt

    # def __keyword_parser(self, message: AIMessage) -> str:
    #     message_string = message.content
    #
    #     logger.debug(f"Full LLM answer: \n {message_string}")
    #
    #     keyword_index = message_string.rfind(self.keyword)
    #     if keyword_index == -1:
    #         return ""
    #     else:
    #         return message_string[keyword_index + len(self.keyword):]

    def __tag_parser(self, message: AIMessage) -> str:
        """
        Parser with new type of prompt, when AI should generate output with HTML tags
        
        :param message: Langchain's AIMessage object
        :return: Cleaned up answer string
        """  # noqa

        message_string = message.content

        class TagParser(HTMLParser):
            answer_data = False
            answer = ""

            def handle_starttag(self, tag, attrs):
                if tag == "ANSWER":
                    self.answer_data = True

            def handle_endtag(self, tag):
                if tag == "ANSWER":
                    self.answer_data = False

            def handle_data(self, data):
                self.answer = str(data)

        parser = TagParser()

        logger.debug(f"Full LLM answer: \n {message_string}")

        parser.feed(message_string)

        if self.no_answer_keyword in parser.answer:
            return ""
        else:
            # TODO: Return with quick cleanup, expand if needed
            return parser.answer.replace("\n", "").strip()

    # TODO: These two functions differ just by options field, can I combine it to one?
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

        chain = prompt | self.llm_chat | self.__tag_parser

        with get_openai_callback() as cb:
            answer = chain.invoke({"resume": str(self.config.user_info),
                                   "question": question})

            logger.warning(f"OpenAI call cost:\n {cb.total_cost}")

        if answer:
            logger.info(f"LLM answer:\n {answer}")
            return True, answer
        else:
            logger.info("LLM did not produce answer!")
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

        chain = prompt | self.llm_chat | self.__tag_parser

        with get_openai_callback() as cb:
            answer = chain.invoke({"resume": str(self.config.user_info),
                                   "question": question,
                                   "options": str(options)})

            logger.warning(f"OpenAI call cost:\n {cb.total_cost}")

        if answer:
            logger.info(f"LLM answer:\n {answer}")
            return True, answer
        else:
            logger.info("LLM did not produce answer!")
            return False, answer
