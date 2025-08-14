# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv


def create_azure_openai_agent(model_name: str, system_prompt: str, tools: list) -> AgentExecutor:
    """Create an agent from a set of tools and an Azure deployment"""
    
    load_dotenv()

    llm = AzureChatOpenAI(azure_deployment=model_name)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create the agent using LangChain's built-in tool handling
    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        name="NotebookPromptAgent",
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent_executor
