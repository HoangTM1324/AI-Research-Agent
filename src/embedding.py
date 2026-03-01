from .schema import GraphState
import hashlib
import chromadb
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter



def generate_chunk_id(content: str):
    """
    Generate a unique chunk ID based on the content using SHA-256 hashing.
    
    Args:
        Input:
            content (str): The text content of the chunk for which to generate an ID.
        Output:
            str: A unique chunk ID derived from the content.
    """

    # Encode the content to bytes
    content_bytes = content.encode('utf-8')
    
    # Create a SHA-256 hash of the content
    hash_object = hashlib.sha256(content_bytes)
    content_hash = hash_object.hexdigest()
    
    return f"chunk_{content_hash[:16]}"

def process_local_pdf_node(state: GraphState):
    file_path = state["file_path"]
    if file_path != "":
        print("--- PROCESSING LOCAL PDF ---")
        loader= PyMuPDFLoader(file_path)
        data= loader.load()

        text_splitter= RecursiveCharacterTextSplitter(chunk_size= 2000, chunk_overlap= 100)

        chunks= text_splitter.split_documents(data)
        chunk_ids = []
        client= chromadb.Client()
        collection= client.get_or_create_collection(name="pdf_chunks")
        for chunk in chunks:
            chunk_id = generate_chunk_id(chunk.page_content)
            chunk_ids.append(chunk_id)
            collection.upsert(documents= chunk.page_content,
                          ids= chunk_id)
        return {"documents": chunks, "ids": chunk_ids}
    else:
        return {"documents": [], "ids": []}
    

