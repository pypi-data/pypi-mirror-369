# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging

from jupyter_kernel_client import KernelClient
from jupyter_nbmodel_client import NbModelClient
from langchain.agents import AgentExecutor, tool

from jupyter_ai_agents.agents.base import RuntimeAgent
from jupyter_ai_agents.agents.utils import create_ai_agent
from jupyter_ai_agents.tools.tools import insert_execute_code_cell_tool
from jupyter_ai_agents.utils import (
    retrieve_cells_content_error,
    retrieve_cells_content_until_first_error,
)

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a powerful coding assistant.
Your goal is to help the user understand the coding error in a notebook and provide a correction.
You will receive the notebook content and error and you will need to insert code cells with the correction and comments to explain the error in a concise way.
Ensure updates to cell indexing when new cells are inserted. Maintain the logical flow of execution by adjusting cell index as needed.
"""


def _create_agent(
    notebook: NbModelClient,
    kernel: KernelClient,
    model_provider: str,
    model_name: str,
    current_cell_index: int,
) -> AgentExecutor:
    """Explain and correct an error in a notebook based on the prior cells."""

    @tool
    def insert_execute_code_cell(cell_index: int, cell_content: str) -> str:
        """Add a Python code cell to the notebook at the given index with a content and execute it."""
        insert_execute_code_cell_tool(notebook, kernel, cell_content, cell_index)
        return "Code cell added and executed."

    tools = [insert_execute_code_cell]

    if current_cell_index != -1:
        cells_content_until_error, error = retrieve_cells_content_error(
            notebook, current_cell_index
        )

        system_prompt_final = f"""
        {SYSTEM_PROMPT}
        
        Notebook content: {cells_content_until_error}
        """
        input = f"Error: {error}"

    else:
        cells_content_until_first_error, first_error = retrieve_cells_content_until_first_error(
            notebook
        )

        system_prompt_final = f"""
        {SYSTEM_PROMPT}
        
        Notebook content: {cells_content_until_first_error}
        """
        input = f"Error: {first_error}"

    logger.debug("Prompt with content", system_prompt_final)
    logger.debug("Input", input)

    return create_ai_agent(model_provider, model_name, system_prompt_final, tools)


async def explain_error(
    notebook: NbModelClient,
    kernel: KernelClient,
    model_provider: str,
    model_name: str,
    current_cell_index: int,
) -> list:
    """Explain and correct an error in a notebook based on the prior cells."""
    agent = _create_agent(notebook, kernel, model_provider, model_name, current_cell_index)
    replies = []
    async for reply in agent.astream({"input": input}):
        replies.append(reply)
    return replies
