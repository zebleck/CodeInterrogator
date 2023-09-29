import streamlit as st
import os
import sys
import logging
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, ServiceContext
from llama_index.llms import OpenAI
import openai

logging.basicConfig(level=logging.INFO)

# API key setup
openai.api_key = st.secrets.openai_key

# Initialize session state
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about LLama index's open-source Python library!"}
    ]

    
@st.cache_resource(show_spinner=False)
def load_data():
	# Get folder path from command-line arguments
	folder_path = sys.argv[-1] if len(sys.argv) > 1 else './results'

	# Get index name from folder name
	index_name = os.path.basename(os.path.normpath(folder_path))
	logging.info(f"Index name: {index_name}")

	index = None
	try:
		# Rebuild storage context
		storage_context = StorageContext.from_defaults(persist_dir='./storage')
		# Load index
		index = load_index_from_storage(storage_context, index_id=index_name)
		logging.info(f"Loaded index: {index}")
		return index
	except Exception as e:
		logging.info(f"Could not load index: {e}\nCreating index...")
		documents = SimpleDirectoryReader(folder_path).load_data()
		service_context = ServiceContext.from_defaults(llm=OpenAI(temperature=0, model="gpt-4"))#, temperature=0.5, system_prompt="You are an expert on the LLama index Python library and your job is to answer technical questions. Assume that all questions are related to the LLama index Python library. Keep your answers technical and based on facts – do not hallucinate features."))

		index = VectorStoreIndex.from_documents(documents, service_context=service_context)
		index.set_index_id(index_name)
		index.storage_context.persist("./storage")
		logging.info(f"Created index: {index}")
		return index

index = load_data()

# Define chat engine
#mode = st.selectbox("Select query mode", ["condense_question", "best", "context", "simple", "react", "openai"])
#chat_engine = index.as_chat_engine(chat_mode=mode, verbose=True)

response_mode = st.selectbox("Select response mode", ["refine", "compact", "tree_summarize", "simple_summarize", "no_text", "accumulate", "compact_accumulate"])

query_engine = index.as_query_engine(response_mode=response_mode, similarity_top_k=5)

logging.info("Response mode: " + response_mode)

# Chat UI
if prompt := st.chat_input("Your question:"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Perform and display the query
if st.session_state.messages[-1]["role"] != "assistant":
	with st.chat_message("assistant"):
		with st.spinner("Thinking..."):
			#response = chat_engine.chat(prompt)
			response = query_engine.query(prompt)
			st.write(response.response)
			st.session_state.messages.append({"role": "assistant", "content": response.response})