import os
import sys
from pathlib import Path

# Ensure project root is on path when running from src/llm (or any subdir)
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from src.llm.prompts import postgres_system_prompt
from src.utils.constants import SQL_LLM_MODEL
from src.database.execute import execute

ollama_api_key=os.getenv("OLLAMA_API_KEY")

def generate_sql(question: str) -> str:
    """Generate a SQL query from a natural language prompt using local Ollama."""
    llm = ChatOllama(model=SQL_LLM_MODEL, api_key=ollama_api_key, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", postgres_system_prompt),
        ("human", "{question}"),
    ])
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content if hasattr(response, "content") else str(response)

def execute_sql(query: str) -> list[dict]:
    """Execute a SQL query and return the results."""
    sql_query = generate_sql(query)
    print(sql_query)
    return execute(sql_query)


# if __name__ == "__main__":
#     question = "How much amount spend on the groceries"
#     print(question)
#     print(execute_sql(question))
