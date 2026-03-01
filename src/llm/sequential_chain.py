"""
Sequential LangChain: data passed from one agent to another.

  User question → Agent 1 (SQL) → SQL string → DB execute → Agent 2 (Analyze) → analysis

Run from project root: uv run python src/llm/sequential_chain.py
"""

import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import ChatOllama

from src.llm.prompts import postgres_system_prompt, analyze_system_prompt
from src.utils.constants import SQL_LLM_MODEL
from src.database.execute import execute

# --- Agent 1: question → SQL ---
sql_prompt = ChatPromptTemplate.from_messages([
    ("system", postgres_system_prompt),
    ("human", "{question}"),
])
sql_llm = ChatOllama(model=SQL_LLM_MODEL, temperature=0)
sql_chain = sql_prompt | sql_llm

# --- Agent 2: question + data → analysis ---
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system", analyze_system_prompt),
    ("human", "Question: {question}\n\nData:\n{financial_data}"),
])
# Use same or different LLM
analyze_llm = ChatOllama(model=SQL_LLM_MODEL, temperature=0)
analyze_chain = analyze_prompt | analyze_llm


def get_sql_content(x: dict) -> dict:
    """Run SQL agent and add sql_query + sql_result to state."""
    out = sql_chain.invoke(x)
    sql_query = out.content if hasattr(out, "content") else str(out)
    rows = execute(sql_query) if sql_query else []
    return {**x, "sql_query": sql_query, "financial_data": str(rows)}


def run_analyzer(x: dict) -> str:
    """Run analyze agent on question + financial_data."""
    out = analyze_chain.invoke({"question": x["question"], "financial_data": x["financial_data"]})
    return out.content if hasattr(out, "content") else str(out)


# Sequential pipeline: question → {question, sql_query, financial_data} → analysis
sequential_chain = (
    RunnablePassthrough()
    | RunnableLambda(get_sql_content)
    | RunnableLambda(run_analyzer)
)


def run_sequential(question: str) -> str:
    """Run both agents in sequence; return final analysis."""
    return sequential_chain.invoke({"question": question})


if __name__ == "__main__":
    q = "How much did I spend at No Frills in Milton?"
    print("Question:", q)
    print("\nAnalysis:\n", run_sequential(q))
