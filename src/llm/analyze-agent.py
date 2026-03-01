import os
import sys
from pathlib import Path

# Ensure project root is on path when running from src/llm (or any subdir)
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.constants import analyze_llm_model
from src.llm.prompts import analyze_system_prompt


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def analyze_data(financial_data: str, question: str) -> str:
    analyze_prompt_template = ChatPromptTemplate.from_messages([
        ("system", analyze_system_prompt),
        ("human", "{question}: {financial_data}"),
    ])
    llm = ChatOpenAI(model=analyze_llm_model, api_key=openai_api_key)
    chain = analyze_prompt_template | llm
    response = chain.invoke({"financial_data": financial_data, "question": question})
    return response.content



# analyze_prompt_template = ChatPromptTemplate.from_messages([
#     ("system", analyze_system_prompt),
#     ("human", "Data about bank transactions: {bank_transactions}"),
# ])

# llm = ChatOpenAI(model=analyze_llm_model, api_key=openai_api_key)

# chain = analyze_prompt_template | llm

# response = chain.invoke({"bank_transactions": ""})
# print(response.content)