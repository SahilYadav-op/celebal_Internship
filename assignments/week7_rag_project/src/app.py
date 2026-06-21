# app.py - Main Streamlit application
# This is the entry point - run with: streamlit run app.py

import streamlit as st
from vectorstore import VectorStore
from chatbot import Chatbot
import tempfile
import os


def main():
    # page config
    st.set_page_config(page_title="Document QA Bot", page_icon="🤖", layout="wide")

    st.title("Document QA Bot 🤖")
    st.write("Upload a PDF, enter your API keys, and ask questions about the document!")

    # setup session state for chat history and other stuff
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "vectorstore" not in st.session_state:
        st.session_state["vectorstore"] = None
    if "chatbot" not in st.session_state:
        st.session_state["chatbot"] = None
    if "doc_processed" not in st.session_state:
        st.session_state["doc_processed"] = False

    # sidebar for API keys
    with st.sidebar:
        st.header("API Keys 🔑")
        st.write("You need both Cohere and Pinecone API keys to use this app.")

        cohere_api_key = st.text_input("Cohere API Key", type="password",
                                        help="Get your key from cohere.com")
        pinecone_api_key = st.text_input("Pinecone API Key", type="password",
                                          help="Get your key from pinecone.io")

        st.markdown("---")
        st.markdown("### How to get API keys:")
        st.markdown("1. **Cohere**: Sign up at [cohere.com](https://cohere.com)")
        st.markdown("2. **Pinecone**: Sign up at [pinecone.io](https://www.pinecone.io)")

        # cleanup button
        if st.session_state["doc_processed"]:
            if st.button("🗑️ Clear & Start Over"):
                if st.session_state["vectorstore"]:
                    st.session_state["vectorstore"].cleanup()
                st.session_state["vectorstore"] = None
                st.session_state["chatbot"] = None
                st.session_state["chat_history"] = []
                st.session_state["doc_processed"] = False
                st.rerun()

    # file upload section
    uploaded_file = st.file_uploader("📄 Upload a PDF file", type="pdf")

    # process the PDF when uploaded
    if uploaded_file and not st.session_state["doc_processed"]:
        if not cohere_api_key or not pinecone_api_key:
            st.warning("⚠️ Please enter both API keys in the sidebar first!")
        else:
            with st.spinner("Processing your document... This might take a minute."):
                try:
                    # save uploaded file to a temp location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    # create vector store (this does all the processing)
                    vs = VectorStore(tmp_path, cohere_api_key, pinecone_api_key)
                    st.session_state["vectorstore"] = vs

                    # create chatbot
                    bot = Chatbot(vs, cohere_api_key)
                    st.session_state["chatbot"] = bot
                    st.session_state["doc_processed"] = True

                    # cleanup temp file
                    os.unlink(tmp_path)

                    st.success(f"✅ Document processed! Found {len(vs.chunks)} text chunks. Ask away!")

                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
                    # cleanup temp file if it exists
                    if 'tmp_path' in locals():
                        os.unlink(tmp_path)

    # show status
    if st.session_state["doc_processed"]:
        st.info(f"📚 Document loaded with {len(st.session_state['vectorstore'].chunks)} chunks")

    # chat section
    st.markdown("---")
    st.subheader("💬 Ask Questions")

    # display chat history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # input for questions
    user_query = st.chat_input("Ask a question about your document...")

    if user_query:
        if not st.session_state["doc_processed"]:
            st.warning("Please upload a PDF document first!")
        else:
            # show user message
            st.chat_message("user").write(user_query)
            st.session_state["chat_history"].append({"role": "user", "content": user_query})

            # get response
            with st.spinner("Thinking..."):
                response = st.session_state["chatbot"].respond(user_query)

            # show response
            st.chat_message("assistant").write(response)
            st.session_state["chat_history"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
