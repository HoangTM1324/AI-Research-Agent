from src.schema import GraphState
from src.retrieve import generate_web_subquestions_node, process_local_pdf_node, web_search_node
print("import successful")

if __name__ == "__main__":
    user_prompt= """What is transformer architecture?"""
    state= GraphState(
        question= user_prompt,
        generation= "",
        web_search= "",
        documents= [],
        file_path= "transformer.pdf"
    )
    docs = process_local_pdf_node(state)
    # print(docs["documents"][0].page_content)
    # print(docs["documents"][0].metadata)
    