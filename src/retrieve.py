import getpass
import os
import hashlib
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import arxiv
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .schema import GraphState
load_dotenv()
# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0)


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


def process_local_pdf_node(state: GraphState):
    print("--- PROCESSING LOCAL PDF ---")
    file_path = state["file_path"]

    
    loader= PyMuPDFLoader(file_path)
    data= loader.load()
    system_prompt= """You are an expert academic search assistant. Your task is to analyze the content of the PDF document and find out the title and authors of the article. Your output should return a string in the format of "title \n Authors" """
    # print(data[0].page_content)
    message = [
        SystemMessage(content= system_prompt),
        HumanMessage(content= f"PDF CONTENT: \n{data[0].page_content}")
    ]
    pdf_info= llm.invoke(message)
    pdf_info= pdf_info.content.strip().split("\n")

    for page in data:
        page.metadata["title"]= pdf_info[0]
        page.metadata["author"]= pdf_info[1]

    text_splitter= RecursiveCharacterTextSplitter(chunk_size= 2000, chunk_overlap= 100)

    chunks= text_splitter.split_documents(data)
    chunk_ids = []
    for c in chunks:
        # Tạo dấu vân tay dựa trên nội dung đoạn văn
        content_hash = hashlib.md5(c.page_content.encode()).hexdigest()
        # ID = tên_file + số_trang + mã_hash
        source_name = c.metadata.get("source", "unknown").split("\\")[-1] # Lấy tên file gọn
        page_num = c.metadata.get("page", 0)
        chunk_id = f"{source_name}_p{page_num}_{content_hash}"
        chunk_ids.append(chunk_id)

    print(f"--- Created {len(chunks)} chunks with unique IDs ---")

    # Trả về documents kèm ids để bước sau nạp vào ChromaDB
    return {"documents": chunks, "ids": chunk_ids}

def web_search_node(content):
    print("---Web Search---")
    web_search_tool = TavilySearchResults(k=3)
    web_results= []
    state= []
    system_prompt= f"""You are an expert academic research assistant. Your task is to determine if the retrieved web search results are relevant to the user's question or not. Your output should return value "relevant" if the retrieved web search results are relevant to user's question. Ortherwise, return "irrelevant". Here is the question: {content}"""
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
     



