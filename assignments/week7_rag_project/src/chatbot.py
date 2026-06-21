# chatbot.py - handles the conversation with Cohere's LLM
# Takes the retrieved chunks from vectorstore and uses them to answer questions

import cohere
import uuid


class Chatbot:
    """
    Simple chatbot class that uses Cohere to generate answers
    It takes retrieved document chunks as context
    """

    def __init__(self, vectorstore, cohere_api_key):
        self.vectorstore = vectorstore
        self.co = cohere.Client(cohere_api_key)
        self.conversation_id = str(uuid.uuid4())  # unique id for this chat session

    def respond(self, user_message):
        """
        Main method - takes user question and returns an answer
        Steps:
        1. Retrieve relevant chunks from vectorstore
        2. Format them as documents for Cohere
        3. Send to Cohere chat API with the documents as context
        """
        # get relevant chunks from the vector store
        retrieved_chunks = self.vectorstore.retrieve(user_message)

        # format chunks as documents that Cohere can use
        # each document needs a snippet field
        documents = []
        for i, chunk in enumerate(retrieved_chunks):
            documents.append({
                "id": str(i),
                "snippet": chunk,
                "title": f"Document Chunk {i+1}"
            })

        # if we didn't find any relevant chunks
        if not documents:
            return "Sorry, I couldn't find relevant information in the document to answer your question. Could you try rephrasing?"

        # call Cohere chat API with the documents
        try:
            response = self.co.chat(
                message=user_message,
                model="command-r-plus",
                documents=documents,
                conversation_id=self.conversation_id,
                temperature=0.3,  # lower temperature for more factual answers
            )

            return response.text

        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Sorry, there was an error generating a response: {str(e)}"
