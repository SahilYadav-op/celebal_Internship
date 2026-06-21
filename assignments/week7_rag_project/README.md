# RAG Document Question Answering System

This project implements a Retrieval-Augmented Generation (RAG) system that answers questions based on custom documents. Instead of relying only on a language model's internal knowledge, the system retrieves relevant information from documents and then generates answers grounded in that information.

**Week 7 - Celebal Technologies Internship**  
**Author**: Sahil Yadav

## Overview

Instead of relying only on a language model's internal knowledge, this system retrieves relevant information from uploaded documents and generates answers grounded in that data. This improves factual accuracy and allows question answering over private or domain-specific data.

You can upload your own PDFs - notes, resume, research papers, books - anything you want to ask questions about.

## Key Concepts

### Retrieval
Retrieval is responsible for finding the most relevant chunks of text from a document. It uses embeddings and vector similarity search. We use Cohere's `embed-english-v3.0` model and Pinecone for vector storage.

### Augmentation
The retrieved content is added to the model's input to provide context for answering. We format the top chunks as documents and pass them to Cohere's chat API.

### Generation
A language model (Cohere `command-r-plus`) generates the final answer using the retrieved context, ensuring responses are grounded in actual data from your documents.

## System Architecture

The pipeline consists of these stages:

```
PDF Upload → Text Extraction → Chunking → Embedding → Vector DB (Pinecone)
                                                            ↓
User Question → Query Embedding → Similarity Search → Reranking → Answer Generation
```

1. **Document Ingestion** - PDFs are loaded and converted into raw text using PyMuPDF
2. **Text Chunking** - Text is split into ~1000 char chunks by sentence boundaries
3. **Embedding Creation** - Each chunk is converted into a 1024-dim vector using Cohere
4. **Vector Database** - Embeddings are stored in Pinecone for similarity search
5. **Query Processing** - User's question is converted into an embedding
6. **Context Retrieval** - Most relevant chunks are retrieved and reranked
7. **Answer Generation** - Cohere's LLM generates an answer using the retrieved context

## Components Used

| Component | Tool | Purpose |
|-----------|------|---------|
| Embedding Model | Cohere embed-english-v3.0 | Converting text into 1024-dim vectors |
| Vector Store | Pinecone (serverless) | Storing and searching embeddings |
| Reranker | Cohere rerank-english-v3.0 | Improving retrieval accuracy |
| Language Model | Cohere command-r-plus | Generating answers from context |
| PDF Reader | PyMuPDF (fitz) | Extracting text from PDFs |
| Frontend | Streamlit | Web interface |

## Project Structure

```
├── src/
│   ├── app.py              # Streamlit web interface (main entry point)
│   ├── vectorstore.py      # PDF processing, embedding, Pinecone indexing, retrieval
│   └── chatbot.py          # Cohere chat with retrieved document context
├── notebook.ipynb          # Step-by-step code walkthrough
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Setup & Usage

### 1. Clone the repo
```bash
git clone <repo-url>
cd week7_rag_project
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get API Keys
- **Cohere**: Sign up at [cohere.com](https://cohere.com) (free trial available)
- **Pinecone**: Sign up at [pinecone.io](https://www.pinecone.io) (free tier available)

### 5. Run the app
```bash
cd src
streamlit run app.py
```

### 6. Use the app
1. Enter your API keys in the sidebar
2. Upload a PDF file
3. Wait for processing (~1 minute)
4. Start asking questions about your document!

## Example Flow

**User Question**: "What is the main idea of the document?"

**System Process**:
1. Embeds the question using Cohere
2. Searches Pinecone for the 10 most similar chunks
3. Reranks to keep the top 3 most relevant
4. Sends chunks + question to Cohere's LLM
5. Returns a concise, grounded answer

## Workflow

1. Load and preprocess PDF documents
2. Split text into chunks (~1000 chars each)
3. Convert chunks into vector embeddings
4. Store embeddings in Pinecone vector database
5. Accept user query via Streamlit chat
6. Retrieve relevant chunks using similarity search + reranking
7. Generate answer using Cohere with retrieved context

## Improvements Implemented

- **Sentence-aware chunking** - splits by sentence boundaries so chunks don't cut mid-sentence
- **Reranking** - uses Cohere's rerank model after initial retrieval for better relevance
- **Batch processing** - handles large documents by processing embeddings in batches of 96
- **Input type optimization** - uses `search_document` for indexing and `search_query` for queries

## Key Learnings

- How RAG systems combine retrieval and generation for accurate answers
- Importance of retrieval quality in improving answer accuracy
- Working with vector embeddings and similarity search
- Handling unstructured text data from PDFs
- Building interactive AI applications with Streamlit
- How reranking significantly improves retrieval precision

## Conclusion

This project demonstrates how to build a system that understands user queries, retrieves relevant information from documents, and generates accurate answers. RAG systems like this are widely used in chatbots, knowledge assistants, enterprise search systems, and AI-powered documentation tools.

## References

- [Cohere RAG Documentation](https://docs.cohere.com/docs/retrieval-augmented-generation-rag)
- [Pinecone Quickstart Guide](https://docs.pinecone.io/guides/get-started/quickstart)
- [Reference Project](https://github.com/VivekChauhan05/RAG_Document_Question_Answering)
