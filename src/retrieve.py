import getpass
import os
import chromadb
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from .schema import GraphState
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0)

def retrieve_from_chromadb_node(state: GraphState):
    print("--- RETRIEVING FROM DATABASE ---")
    client= chromadb.Client()
    collection= client.get_or_create_collection(name="pdf_chunks")
    query= state["question"]
    results= collection.query(query_texts= query, n_results= 3)
    if not results["documents"] or len(results["documents"][0]) == 0:
        print("--- NO DOCUMENTS FOUND IN DB ---")
        return {"documents": []}
    return {"documents": results["documents"][0]}

def generate_web_subquestions_node(state: GraphState):
    user_input = state["question"]

    system_prompt = """You are an expert academic research assistant. Your task is to analyze the user's input question and generate 3 distinct sub-questions in English to optimize information retrieval from the web.

    Each sub-question should focus on a different aspect:

    1. Core Mechanism: How the technology or concept works fundamentally.

    2. Context & Evolution: The history, origin, or comparative state-of-the-art.

    3. Applications & Limitations: Practical use cases or existing challenges.

    Output only the questions, one per line, without numbering or extra commentary."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]

    response = llm.invoke(messages)
    content = response.content.split("\n")
    return {"subquestions": content}


def web_search_node(state: GraphState):
    print("--- Web Search ---")
    web_search_tool = TavilySearchResults(k=1)
    web_results= []
    for c in state["subquestions"]:
        search_data = web_search_tool.invoke(c)
        web_results.append(search_data)
    return {"web_search": web_results}
     



