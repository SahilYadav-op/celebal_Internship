# vectorstore.py - handles all the PDF processing and vector stuff
# Using Cohere for embeddings and Pinecone for storing vectors

import cohere
import fitz  # this is PyMuPDF, weird import name but it works
from pinecone import Pinecone, ServerlessSpec
import uuid
import time


class VectorStore:
    """
    This class does all the heavy lifting for RAG:
    1. Reads PDF and extracts text
    2. Splits text into chunks
    3. Creates embeddings using Cohere
    4. Stores them in Pinecone
    5. Retrieves relevant chunks for a query
    """

    def __init__(self, pdf_path, cohere_api_key, pinecone_api_key):
        self.pdf_path = pdf_path
        self.co = cohere.Client(cohere_api_key)
        self.pinecone_api_key = pinecone_api_key
        self.chunks = []
        self.embeddings = []
        self.retrieve_top_k = 10  # how many chunks to fetch initially
        self.rerank_top_k = 3    # how many to keep after reranking

        # run the whole pipeline
        print("Loading PDF...")
        self.load_pdf()
        print(f"Splitting text into chunks...")
        self.split_text()
        print(f"Got {len(self.chunks)} chunks")
        print("Creating embeddings...")
        self.embed_chunks()
        print("Indexing in Pinecone...")
        self.index_chunks()
        print("Done! Ready to answer questions.")

    def load_pdf(self):
        """Extract all text from the PDF file"""
        self.pdf_text = self.extract_text_from_pdf(self.pdf_path)

    def extract_text_from_pdf(self, pdf_path):
        """Uses PyMuPDF to read each page of the PDF"""
        text = ""
        try:
            with fitz.open(pdf_path) as pdf:
                for page_num in range(pdf.page_count):
                    page = pdf.load_page(page_num)
                    text += page.get_text("text")
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
        return text

    def split_text(self, chunk_size=1000):
        """
        Split the text into smaller chunks
        We split by sentences first, then group them into chunks of ~1000 chars
        This way we don't cut sentences in half
        """
        sentences = self.pdf_text.split(". ")
        current_chunk = ""

        for sentence in sentences:
            # if adding this sentence would make the chunk too big, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                self.chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk += sentence + ". "

        # don't forget the last chunk
        if current_chunk.strip():
            self.chunks.append(current_chunk.strip())

    def embed_chunks(self):
        """
        Create vector embeddings for each chunk using Cohere
        We use embed-english-v3.0 which gives 1024-dim vectors
        input_type="search_document" tells Cohere these are docs being indexed
        """
        # Cohere has a limit on batch size, so we process in batches of 96
        batch_size = 96
        all_embeddings = []

        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i + batch_size]
            response = self.co.embed(
                texts=batch,
                model="embed-english-v3.0",
                input_type="search_document"
            )
            all_embeddings.extend(response.embeddings)

        self.embeddings = all_embeddings

    def index_chunks(self):
        """Store the embeddings in Pinecone so we can search them later"""
        pc = Pinecone(api_key=self.pinecone_api_key)

        # create a unique index name so we don't clash with other projects
        self.index_name = "rag-doc-qa-" + str(uuid.uuid4())[:8]

        # check if index already exists (shouldn't but just in case)
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if self.index_name in existing_indexes:
            pc.delete_index(self.index_name)

        # create the index - using cosine similarity and 1024 dimensions (Cohere embed v3)
        pc.create_index(
            name=self.index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        # wait for index to be ready
        while not pc.describe_index(self.index_name).status['ready']:
            time.sleep(1)

        self.index = pc.Index(self.index_name)

        # upsert vectors in batches
        vectors_to_upsert = []
        for i, (chunk, embedding) in enumerate(zip(self.chunks, self.embeddings)):
            vectors_to_upsert.append({
                "id": str(i),
                "values": embedding,
                "metadata": {"text": chunk}
            })

        # upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)

        # small delay to let pinecone process
        time.sleep(2)

    def retrieve(self, query):
        """
        Given a user query:
        1. Embed the query
        2. Search Pinecone for similar chunks
        3. Rerank results using Cohere rerank for better accuracy
        """
        # embed the query - note input_type is "search_query" not "search_document"
        query_embedding = self.co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        ).embeddings[0]

        # search pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=self.retrieve_top_k,
            include_metadata=True
        )

        # get the text chunks from results
        retrieved_chunks = []
        for match in results['matches']:
            retrieved_chunks.append(match['metadata']['text'])

        # rerank using Cohere for better results
        if retrieved_chunks:
            reranked = self.co.rerank(
                query=query,
                documents=retrieved_chunks,
                top_n=self.rerank_top_k,
                model="rerank-english-v3.0"
            )

            # get the reranked texts
            final_chunks = []
            for result in reranked.results:
                final_chunks.append(retrieved_chunks[result.index])

            return final_chunks

        return retrieved_chunks

    def cleanup(self):
        """Delete the Pinecone index when we're done"""
        try:
            pc = Pinecone(api_key=self.pinecone_api_key)
            pc.delete_index(self.index_name)
            print(f"Cleaned up index: {self.index_name}")
        except Exception as e:
            print(f"Couldn't clean up index: {e}")
