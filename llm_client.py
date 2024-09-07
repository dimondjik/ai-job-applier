from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config_manager import ConfigManager


class ChatOpenAIWrapper:
    def __init__(self):
        self.config = ConfigManager()
        self.llm_chat = ChatOpenAI(model="gpt-4o",
                                   openai_api_key=self.config.openai_api_key,
                                   temperature=0.8)

    def invoke(self, messages):
        return self.llm_chat.invoke(messages)


if __name__ == "__main__":
    llm = ChatOpenAIWrapper()
    print(llm.invoke(messages=[SystemMessage("You are a helpful assistant"),
                        HumanMessage("Hi! What is the capital of France?")]))
