# AI Research Assistant (Dockerized) DEV BRANCH

This project is a sophisticated **AI Research Assistant** built with a **FastAPI** backend and a **React (TypeScript)** frontend. It leverages **LangGraph** for advanced RAG (Retrieval-Augmented Generation) workflows, allowing users to analyze local PDFs and perform real-time web research using **Gemini** and **Tavily**.

---

Now I change the agent with itself corrective ability called Corrective RAG, as below:

```mermaid
graph TD
	__start__([START]) --> categorizer_node
	
	categorizer_node -.->|pdf| process_local_pdf_node
	categorizer_node -.->|db| retrieve_from_qdrant_node
	
	process_local_pdf_node --> retrieve_from_qdrant_node
	retrieve_from_qdrant_node --> check_retrieve_doc_node
	
	check_retrieve_doc_node -.->|web_retrieve| generate_web_subquestions_node
	check_retrieve_doc_node -.->|gen_answer| generate_answer_node
	
	generate_web_subquestions_node --> web_search_node
	web_search_node --> check_web_search_node
	
	check_web_search_node -.->|generate_subquestions| generate_web_subquestions_node
	check_web_search_node -.->|generate_answer| generate_answer_node
	
	generate_answer_node --> __end__([END])

	style check_web_search_node stroke:#d4a017
```