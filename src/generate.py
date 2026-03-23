from .schema import GraphState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model= "gemini-2.5-flash", temperature= 0, streaming= True)



def generate_answer_node(state: GraphState):
    system_prompt= """You are an expert academic research assistant. Your task is to generate a comprehensive and accurate answer to the user's question based on the retrieved content from the database. Your answer should be well-structured, concise, and directly address the user's question."""
    user_prompt= f"""Here is the user's question: {state["question"]}. Here is the retrieved content {state["documents"]} and result from external web {state["web_search"]}."""
    message= [
        SystemMessage(content= system_prompt), 
        HumanMessage(content= user_prompt)
    ]
    response = llm.invoke(message).content.strip()
    return {"generation": response}
    


