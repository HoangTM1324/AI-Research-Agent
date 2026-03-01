from .schema import GraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model= "gemini-2.5-flash", temperature= 0)

def check_content_from_db_retrieve_node(state: GraphState):
    system_prompt = """You are an expert academic research assistant. Your task is to determine whether the retrieved content from the database is relevant to the user's question. Your output should a result where each element is either "relevant" if the retrieved content is relevant to the user's question, or "irrelevant" if it is not, each result divide by a newline."""
    user_prompt= f"""Here is the user's question: {state["question"]}. Here is the retrieved content from the database:: {state["documents"]}"""
    message= [
        SystemMessage(content= system_prompt),
        HumanMessage(content= user_prompt)
    ]
    response= llm.invoke(message).strip().split("\n")
    new_docs= []
    for doc, res in zip(state["documents"], response):
        if res.lower() == "relevant":
            new_docs.append(doc)
    return {"documents": new_docs}


def generate_answer_node(state: GraphState):
    system_prompt= """You are an expert academic research assistant. Your task is to generate a comprehensive and accurate answer to the user's question based on the retrieved content from the database. Your answer should be well-structured, concise, and directly address the user's question."""
    user_prompt= f"""Here is the user's question: {state["question"]}. Here is the retrieved content {state["documents"]}."""
    message= [
        SystemMessage(content= system_prompt), 
        HumanMessage(content= user_prompt)
    ]
    response= llm.invoke(message).stript()
    return {"generation": response}
    


