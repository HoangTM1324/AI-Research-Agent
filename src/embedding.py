from .schema import GraphState
import hashlib
import uuid
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
client= QdrantClient(url= os.getenv("QDRANT_HOST"), api_key= os.getenv("QDRANT_API_KEY"))
embeddings= GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", output_dimensionality=768)

def process_local_pdf_node(state: GraphState):
    file_path = state["file_path"]
    if file_path != "":
        print("--- PROCESSING LOCAL PDF ---")
        loader= PyMuPDFLoader(file_path)
        data= loader.load()

        text_splitter= RecursiveCharacterTextSplitter(chunk_size= 2000, chunk_overlap= 100)

        chunks= text_splitter.split_documents(data)
        chunk_ids = []
        data= [d.page_content for d in chunks]
        if not client.collection_exists(collection_name="pdf_chunk"):
            collection= client.create_collection(collection_name="pdf_chunk",
                                                 vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE))
        vectors= embeddings.embed_documents(data)

        points= []
        for i, chunk in enumerate(chunks):
            point = models.PointStruct(
                id = str(uuid.uuid5(uuid.NAMESPACE_DNS ,chunk.page_content)),
                vector= vectors[i],
                payload= {"text": chunk.page_content}
            )
            points.append(point)
            
        client.upsert(collection_name= "pdf_chunk", points= points)

        

        return {"file_path": ""}
    else:
        return {"file_path": ""}
    

