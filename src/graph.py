from .retrieve import generate_web_subquestions_node, web_search_node, retrieve_from_qdrant_node, check_web_search_node, check_retrieve_doc_node
from .embedding import process_local_pdf_node
from .schema import GraphState
from .generate import generate_answer_node
from langgraph.graph import END, StateGraph, START

def categorizer_node(state: GraphState):
    return state

def check_resource_node(state: GraphState):
    if state["file_path"] == "":
        return "db"
    return "pdf"

def check_is_enough_doc_node(state: GraphState):
    if len(state["documents"]) < 5:
        return "web_retrieve"
    return "gen_answer"

def decide_to_generate_node(state: GraphState):
    if state["web_search"]:
        return "generate_answer"
    
    if state["loop_step"] < 3:
        return "generate_subquestions"
    
    return "generate_answer"



def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("categorizer_node", categorizer_node)
    workflow.add_node("process_local_pdf_node", process_local_pdf_node)
    workflow.add_node("check_retrieve_doc_node" ,check_retrieve_doc_node)
    workflow.add_node("retrieve_from_qdrant_node", retrieve_from_qdrant_node)
    workflow.add_node("generate_web_subquestions_node", generate_web_subquestions_node)
    workflow.add_node("web_search_node", web_search_node)
    workflow.add_node("check_web_search_node", check_web_search_node)
    workflow.add_node("generate_answer_node", generate_answer_node)

    workflow.add_edge(START, "categorizer_node")
    workflow.add_conditional_edges("categorizer_node", 
                                  check_resource_node, 
                                  {
                                      "pdf": "process_local_pdf_node", 
                                      "db": "retrieve_from_qdrant_node"}
                                  )
    
    workflow.add_edge("process_local_pdf_node", "retrieve_from_qdrant_node")
    workflow.add_edge("retrieve_from_qdrant_node", "check_retrieve_doc_node")

    workflow.add_conditional_edges("check_retrieve_doc_node", check_is_enough_doc_node,
                                   {
                                       "web_retrieve": "generate_web_subquestions_node",
                                       "gen_answer": "generate_answer_node"
                                   })

    workflow.add_edge("generate_web_subquestions_node", "web_search_node")
    workflow.add_edge("web_search_node" ,"check_web_search_node")
    workflow.add_conditional_edges("check_web_search_node", decide_to_generate_node,
                                   {
                                       "generate_answer": "generate_answer_node",
                                       "generate_subquestions": "generate_web_subquestions_node"
                                   })
    workflow.add_edge("generate_answer_node", END)
    
    return workflow.compile()


