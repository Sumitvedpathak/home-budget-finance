import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.utils.constants import SQL_LLM_MODEL

def generate_sql(prompt: str) -> str:
    """Generate a SQL query from a natural language prompt."""
    llm = ChatOpenAI(model=SQL_LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(prompt)
    return llm.invoke(prompt)

if __name__ == "__main__":
    prompt = "Get me the secode heighest salary in the company"
    print(generate_sql(prompt))