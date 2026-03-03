// Denify Interface data
export interface ChatRequest {
    question: string;
    file_path?: string;
}

export interface ChatResponse {
    answer: string;
    error?: string;
}

const API_URL = "http://localhost:8000";

// Send question to python
export const sendChat= async (data: ChatRequest): Promise<ChatResponse> => {
    const response= await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        }, 
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error("Backend connection fail");
    }

    return response.json()
}

// Send pdf to Python
export const uploadFile= async (file : File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response= await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData 
    });

    return response.json();
}


