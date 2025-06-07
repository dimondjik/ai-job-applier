from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from config_manager import ConfigManager
from langchain_core.messages import AIMessage
import logging
from html.parser import HTMLParser
from custom_exceptions import LLMException, CustomExceptionData
from custom_types import *

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


class ChatDeepSeekWrapper:
    def __init__(self):
        """
        Langchain's ChatDeepSeek class with some additional functionality  
        """  # noqa

        self.config = ConfigManager()
        self.llm_chat = ChatDeepSeek(model="deepseek-chat",
                                     temperature=0.32,
                                     api_key=self.config.deepseek_api_key)

    def invoke(self, messages):
        logger.info("Calling DeepSeek")
        return self.llm_chat.invoke(messages)

    def __call__(self, messages):
        return self.invoke(messages)


class LLMClient:
    def __init__(self):
        self.llm_chat = ChatDeepSeekWrapper()
        self.config = ConfigManager()
        self.no_answer_keyword = "CANDIDATE_NO_DATA"
        self.key_tag = "ANSWER"

        self.exception_data = CustomExceptionData()

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
                if tag == "answer":
                    self.answer_data = True

            def handle_endtag(self, tag):
                if tag == "answer":
                    self.answer_data = False

            def handle_data(self, data):
                self.answer = str(data)

        parser = TagParser()

        logger.debug(f"Full LLM answer: \n {message_string}")

        parser.feed(message_string)

        if self.no_answer_keyword in parser.answer:
            self.exception_data.reason = "LLM did not produce an answer!"
            self.exception_data.llm_answer = message_string
            raise LLMException(self.exception_data.reason, self.exception_data)
        else:
            # Return with quick cleanup, expand if needed
            # It should not be here!
            # return parser.answer.replace("\n", "").strip()
            return parser.answer

    # TODO: These two functions differ just by options field, can I combine it to one?
    def answer_freely(self, question: str) -> str:
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

            logger.warning(f"Call cost: {cb.total_cost}")

        # TODO: Return with quick cleanup, expand if needed
        answer = answer.replace("\n", "").strip()

        logger.info(f"The question: {question}\n"
                    f"LLM answer: {answer}")

        return answer

    def answer_with_options(self, question: str, options: list[str]) -> str:
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

            logger.warning(f"Call cost: {cb.total_cost}")

        # TODO: Return with quick cleanup, expand if needed
        answer = answer.replace("\n", "").strip()

        logger.info(f"The question: {question}\n "
                    f"LLM answer: {answer}")

        return answer

    def cv_fill_in(self, job_data: Job, resume_part: str) -> str:
        """
        Answer on question from options provided

        Boolean shows if LLM was able to answer a question

        :param job_data:
        :param resume_part:

        :return: Call result and answer
        """
        prompt = self.__build_prompt(self.config.prompt_cv_fill_in)

        logger.debug("Full LLM prompt: \n {}".format(
            prompt.invoke({"resume_part": resume_part,
                           "position": job_data.desc,
                           "resume": str(self.config.user_info)})))

        chain = prompt | self.llm_chat | self.__tag_parser

        with get_openai_callback() as cb:
            answer = chain.invoke({"resume_part": resume_part,
                                   "position": job_data.desc,
                                   "resume": str(self.config.user_info)})

            logger.warning(f"Call cost: {cb.total_cost}")

        # TODO: Return with quick cleanup, expand if needed
        answer = answer.strip()

        logger.info(f"Resume part: {resume_part}\n "
                    f"LLM tailored part: {answer}")

        return answer
