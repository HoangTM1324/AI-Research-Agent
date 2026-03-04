from .retrieve import generate_web_subquestions_node, web_search_node, retrieve_from_chromadb_node
from .embedding import process_local_pdf_node
from .schema import GraphState
from .generate import generate_answer_node, check_content_from_db_retrieve_node
from langgraph.graph import END, StateGraph, START

def categorizer_node(state: GraphState):
    return state

def check_resource_node(state: GraphState):
    if state["file_path"] == "":
        return "web"
    return "pdf"


def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("categorizer", categorizer_node)
    workflow.add_node("local_pdf", process_local_pdf_node)
    workflow.add_node("retrieve_db", retrieve_from_chromadb_node)
    workflow.add_node("check_db_retrieve", check_content_from_db_retrieve_node)
    workflow.add_node("generate_subquestions", generate_web_subquestions_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate_answer", generate_answer_node)

    workflow.add_edge(START, "categorizer")
    workflow.add_conditional_edges("categorizer", 
                                  check_resource_node, 
                                  {
                                      "pdf": "local_pdf", 
                                      "web": "retrieve_db"}
                                  )
    
    workflow.add_edge("local_pdf", "generate_subquestions")
    workflow.add_edge("generate_subquestions", "web_search")
    workflow.add_edge("retrieve_db", "check_db_retrieve")
    workflow.add_edge("check_db_retrieve", "generate_subquestions")
    workflow.add_edge("web_search", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()


