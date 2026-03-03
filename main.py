from src.schema import GraphState
from src.graph import build_graph
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import shutil


app = FastAPI()
graph_app = build_graph()


initial_input = {
    "question": "",
    "generation": "",
    "web_search": "",
    "documents": [],
    "file_path": "",
    "subquestions": [] 
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
class ChatRequest(BaseModel):
    question: str
    file_path: Optional[str] = None
    
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def Upload_pdf(file: UploadFile= File(...)):
    if not file.filename.endswith(".pdf"):
        return {"Error": "Must be PDF extension file"}

    file_path= os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_path": file.filename}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    full_path= ""
    if request.file_path:
        full_path= os.path.join(UPLOAD_DIR, request.file_path)

    initial_input["question"]= request.question
    initial_input["file_path"]= full_path

    final_state= await graph_app.ainvoke(initial_input)

    return {"answer": final_state["generation"]}



# print("--- ĐANG CHẠY GRAPH ---")
# final_state = app.invoke(initial_input)

# print("\n--- KẾT QUẢ CUỐI CÙNG ---")

