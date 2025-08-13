from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI
from unified_agent_interface.utils import patch_log

load_dotenv()

# Persistently patch key LangChain calls to log via UAI
patch_log(LLMChain.invoke, label="langchain", capture_return=False)
patch_log(ChatOpenAI.invoke, label="langchain", capture_return=True)

prompt = ChatPromptTemplate(
    [
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)

chain = LLMChain(
    llm=ChatOpenAI(),
    prompt=prompt,
    memory=memory,
)


# if __name__ == "__main__":
#     result = chain.invoke({"text": "my name is bob"})
#     print(result)
#     result = chain.invoke({"text": "what is my name?"})
#     print(result)
