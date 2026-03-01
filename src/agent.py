import os
import sys
from pathlib import Path

# Project root: from src/agent.py go up one level (src -> budget-finance)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))  

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from src.llm.prompts import postgres_system_prompt, analyze_system_prompt
from src.utils.constants import SQL_LLM_MODEL, ANALYZE_LLM_MODEL
from src.database.execute import execute

ollama_api_key=os.getenv("OLLAMA_API_KEY")
openai_api_key=os.getenv("OPENAI_API_KEY")

sql_prompt_template = ChatPromptTemplate.from_messages([
    ("system", postgres_system_prompt),
    ("human", "Question: {question}"),
])

sql_llm = ChatOllama(model=SQL_LLM_MODEL, api_key=ollama_api_key)
sql_chain = sql_prompt_template | sql_llm

def get_sql_content(x: dict) -> dict:
    question = x["question"]
    print(f"Question: {question}")
    out = sql_chain.invoke({"question": question})
    sql_query = out.content if hasattr(out, "content") else str(out)
    print(f"SQL Query: {sql_query}")
    rows = execute(sql_query) if sql_query else []
    print(f"Financial Data: {rows}")
    return {**x, "sql_query": sql_query, "financial_data": str(rows)}



analyze_prompt_template = ChatPromptTemplate.from_messages([
    ("system", analyze_system_prompt),
    ("human", "Question: {question}\n\nData: {financial_data}"),
])

analyze_llm = ChatOllama(model=ANALYZE_LLM_MODEL, api_key=openai_api_key, temperature=0)
analyze_chain = analyze_prompt_template | analyze_llm

def analyze_data(x: dict) -> dict:
    question = x["question"]
    print(f"Question: {question}")
    financial_data = x["financial_data"]
    print(f"Financial Data: {financial_data}")
    out = analyze_chain.invoke({"question": question, "financial_data": financial_data})
    print(f"Output: {out}")
    print(f"Analysis: {out.content if hasattr(out, "content") else str(out)}")
    return {**x, "analysis": out.content if hasattr(out, "content") else str(out)} 


sequential_chain = (
    RunnablePassthrough()
    | RunnableLambda(get_sql_content)
    # | RunnableLambda(analyze_data)
)

response = sequential_chain.invoke({"question": "How much did I spend at No Frills?"})
print("Final Response: ", response)