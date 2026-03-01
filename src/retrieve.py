import getpass
import os
import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import arxiv
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from .schema import GraphState
load_dotenv()
# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0)

def retrieve_from_chromadb_node(state: GraphState):
    print("--- RETRIEVING FROM DATABASE ---")
    client= chromadb.Client()
    collection= client.get_or_create_collection(name="pdf_chunks")
    query= state["question"]
    results= collection.query(query_texts= query, n_results= 3)
    return results["documents"][0]

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
    print(response.content)
    content = response.content.split("\n")
    return content


def web_search_node(state: GraphState):
    print("--- Web Search ---")
    web_search_tool = TavilySearchResults(k=3)
    web_results= []
    state= []
    system_prompt= f"""You are an expert academic research assistant. Your task is to determine if the retrieved web search results are relevant to the user's question or not. Your output should return value "relevant" if the retrieved web search results are relevant to user's question. Ortherwise, return "irrelevant". Here is the question: {content}"""
    content = generate_web_subquestions_node(state)
    for c in content:
        search_data = web_search_tool.invoke(c)
        web_results.append(search_data)
        merged_content = "\n\n".join([res['content'] for res in search_data])
        message= [
            SystemMessage(content= system_prompt.format(content= content)),
            HumanMessage(content=f"RESEARCH DATA FOUND:\n\n{merged_content}")
        ]
        state.append(llm.invoke(message).content.strip())
    return web_results, state
     



