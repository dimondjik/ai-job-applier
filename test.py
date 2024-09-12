from llm_client import LLMClient

if __name__ == "__main__":
    llm = LLMClient()
    print(llm.answer_freely("How many years of work experience do you have with C++?"))
