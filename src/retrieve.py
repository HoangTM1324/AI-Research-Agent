import getpass
import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from .schema import GraphState
load_dotenv()


from qdrant_client import QdrantClient
embeddings= GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", output_dimensionality=768)

client= QdrantClient(url= os.getenv("QDRANT_HOST"), api_key= os.getenv("QDRANT_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0)

generated_sub_question= []

def retrieve_from_qdrant_node(state: GraphState):
    print("--- RETRIEVING FROM DATABASE ---")
    client= QdrantClient(url= os.getenv("QDRANT_HOST"), api_key= os.getenv("QDRANT_API_KEY"))

    if not client.collection_exists("pdf_chunk"):
        return {"documents": []}
    
    question_vector = embeddings.embed_query(state["question"])

    search_result= client.query_points(
        collection_name="pdf_chunk",
        query=question_vector,
        limit=7
    )

    retrieved_docs = [
    Document(page_content=hit.payload["text"]) 
    for hit in search_result.points
    ]

    return {"documents": retrieved_docs}

def generate_web_subquestions_node(state: GraphState):
    user_input = state["question"]
    loopstep = int(state["loop_step"])
    if not state["subquestions"]:
        system_prompt = """You are an expert academic research assistant. Your task is to analyze the user's input question and generate 3 distinct sub-questions in English to optimize information retrieval from the web.

        Each sub-question should focus on a different aspect:

        1. Core Mechanism: How the technology or concept works fundamentally.

        2. Context & Evolution: The history, origin, or comparative state-of-the-art.

        3. Applications & Limitations: Practical use cases or existing challenges.

        Output only the questions, one per line, without numbering or extra commentary."""

        
    
    else:
        system_prompt = f"""You are an expert academic research assistant. 
        Previous search attempts using these questions: {state['subquestions']} failed to find relevant information.
    
        Your task is to REGENERATE 3 new, different sub-questions. 
        CRITICAL: 
        - Do not repeat or rephrase the previous questions.
        - Shift your perspective (e.g., if you searched for 'how it works', now search for 'real-world use cases' or 'technical specifications').
        - Focus on the main idea: {state['question']}.
        
        Output only the questions, one per line."""
        loopstep +=1

    messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]

    response = llm.invoke(messages)
    content = [line.strip() for line in response.content.strip().split("\n") if line.strip()]    
    return {"subquestions": content, "loop_step": loopstep}


def web_search_node(state: GraphState):
    print("--- Web Search ---")
    web_search_tool = TavilySearchResults(k=1)
    web_results= []
    for c in state["subquestions"]:
        search_data = web_search_tool.invoke(c)
        web_results.extend(search_data)
    return {"web_search": web_results}
     
def check_web_search_node(state: GraphState):
    print("--- ĐANG ĐÁNH GIÁ KẾT QUẢ TÌM KIẾM ---")
    
    formatted_docs = "\n\n".join([f"Doc {i+1}: {doc.page_content}" for i, doc in enumerate(state["documents"])])
    
    system_prompt = f"""You are a relevance grader. 
    Your task is to judge if the retrieved documents are useful to answer the user question: {state["question"]}
    For each document, strictly return 'relevant' or 'irrelevant' separated by a newline.
    Do not add any preamble or explanation."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Retrieved Documents:\n{formatted_docs}")
    ]

    response = llm.invoke(messages)
    content = [line.strip().lower() for line in response.content.strip().split('\n') if line.strip()]

    relevant_docs = []
    for doc, label in zip(state["documents"], content):
        if "relevant" in label:
            relevant_docs.append(doc)

    new_step = state.get("loop_step", 0)
    if len(relevant_docs) == 0:
        new_step += 1

    return {"documents": relevant_docs, "loop_step": new_step}
    
    

def check_retrieve_doc_node(state: GraphState):
    formatted_input = "\n\n".join([f"Paragraph {i+1}: {doc.page_content}" for i, doc in enumerate(state["documents"])])

    system_prompt = f"""You are an expert academic research assistant. 
    User will give you a list of paragraphs retrieved by the question. 
    
    Your task is to determine whether each of the provided paragraphs is relevant to the user's question.    
    
    For each paragraph, strictly return ONLY the word 'relevant' or 'irrelevant'.  
    Your each answer must divide by '\n'. Do not include any other text or explanations.

    Here is the question: {state["question"]}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Retrieved Paragraphs:\n{formatted_input}")
    ]

    response = llm.invoke(messages)

    raw_content = response.content.strip().split('\n')
    results = [line.strip().lower() for line in raw_content if line.strip()]

    filter_docs= []
    for (doc, isRelevant) in zip(state["documents"], results):
        if isRelevant == "relevant":
            filter_docs.append(doc)
    
    return {"documents": filter_docs}


