from typing import List, TypedDict
from langchain_core.documents import Document

class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    file_path: str
    subquestions: List[str]