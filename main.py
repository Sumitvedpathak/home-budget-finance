from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import os
from src.llm.prompts import postgres_system_prompt
from src.utils.constants import SQL_LLM_MODEL

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


# if __name__ == "__main__":
#     question = "Get me the second highest salary in the company"
#     print("Question:", question)
#     try:
#         sql = generate_sql(question)
#         print("SQL:", sql)
#     except Exception as e:
#         print("Error:", e)
