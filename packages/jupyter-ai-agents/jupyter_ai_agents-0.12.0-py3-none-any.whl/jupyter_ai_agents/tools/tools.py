# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

from jupyter_nbmodel_client import NbModelClient
from jupyter_kernel_client import KernelClient


def add_markdown_cell_tool(notebook: NbModelClient, cell_content: str) -> None:
    """Add a Markdown cell with a content to the notebook."""
    notebook.add_markdown_cell(cell_content)


def insert_markdown_cell_tool(notebook: NbModelClient, cell_content: str, cell_index:int) -> None:
    """Insert a Markdown cell with a content at a specific index in the notebook."""
    notebook.insert_markdown_cell(cell_index, cell_content)


def add_execute_code_cell_tool(notebook: NbModelClient, kernel: KernelClient, cell_content: str) -> None:
    """Add a Python code cell with a content to the notebook and execute it."""
    cell_index = notebook.add_code_cell(cell_content)
    results = notebook.execute_cell(cell_index, kernel)
    assert results["status"] == "ok"


def insert_execute_code_cell_tool(notebook: NbModelClient, kernel: KernelClient | None, cell_content: str, cell_index:int) -> None:
    """Insert a Python code cell with a content at a specific index in the notebook and execute it."""
    notebook.insert_code_cell(cell_index, cell_content)
    if kernel is not None:
        results = notebook.execute_cell(cell_index, kernel)
        assert results["status"] == "ok"
