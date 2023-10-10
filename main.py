import streamlit as st
import os
import sys
import logging
from llama_index import TreeIndex, SimpleDirectoryReader, StorageContext, get_response_synthesizer, load_index_from_storage, ServiceContext
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.text_splitter import CodeSplitter
from llama_index.node_parser import SimpleNodeParser
import openai
import json
import nest_asyncio

nest_asyncio.apply()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger()

if not logger.handlers:
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# API key setup
openai.api_key = st.secrets.openai_key

# Get folder path from command-line arguments
folder_path = sys.argv[-1] if len(sys.argv) > 1 else './results'

# Get index name from folder name
index_name = os.path.basename(os.path.normpath(folder_path))

    
@st.cache_resource(show_spinner=False)
def load_data():

	index = None
	try:
		# Rebuild storage context
		storage_context = StorageContext.from_defaults(persist_dir=f'./storage/{index_name}')
		# Load index
		index = load_index_from_storage(storage_context, index_id=index_name)
		logging.info(f"Loaded index: {index}")
		return index
	except Exception as e:
		logging.info(f"Could not load index: {e}\nCreating new index")# with summary query: {SUMMARY_QUERY}")

		documents = SimpleDirectoryReader(folder_path, recursive=True).load_data()
		service_context = ServiceContext.from_defaults(llm=OpenAI(temperature=0, model="gpt-4"))#, temperature=0.5, system_prompt="You are an expert on the LLama index Python library and your job is to answer technical questions. Assume that all questions are related to the LLama index Python library. Keep your answers technical and based on facts – do not hallucinate features."))

		text_splitter = CodeSplitter(
		language="python",
		chunk_lines=40,
		chunk_lines_overlap=15,
		max_chars=1500,
		)

		node_parser = SimpleNodeParser.from_defaults(text_splitter=text_splitter)
		service_context = ServiceContext.from_defaults(node_parser=node_parser)

		index = TreeIndex.from_documents(documents, service_context=service_context)
		index.set_index_id(index_name)
		index.storage_context.persist(f"./storage/{index_name}")
		logging.info(f"Created index: {index}")
		return index

index = load_data()


# Define chat engine
#mode = st.selectbox("Select query mode", ["condense_question", "best", "context", "simple", "react", "openai"])
#chat_engine = index.as_chat_engine(chat_mode=mode, verbose=True)

response_mode = st.selectbox("Select chat mode", ["best", "context", "condense_question", "simple", "react", "openai"])

# assemble query engine
chat_engine = index.as_chat_engine(chat_mode=response_mode, verbose=True)

st.subheader("Chat with {0} index".format(index_name))

# Initialize session state
if "messages" not in st.session_state.keys():
    st.session_state.messages = []

# Chat UI
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Perform and display the query
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] != "assistant":
	with st.chat_message("assistant"):
		response = None
		with st.spinner("Thinking..."):
			
			logging.info(prompt)
			# Initialize an empty string to hold the concatenated tokens
			concatenated_response = ""

			# Use stream_chat for streaming response
			response = chat_engine.stream_chat(prompt)

		message_placeholder = st.empty()
		full_response = ""

		for token in response.response_gen:
			full_response += token
			message_placeholder.write(full_response + "▌")
		message_placeholder.write(full_response)
		st.session_state.messages.append({"role": "assistant", "content": full_response})

# Button to export chat log
if len(st.session_state.messages) > 0 and st.button('Export Chat Log'):
    chat_log_str = json.dumps(st.session_state.messages, indent=4)
    st.download_button(
        label="Download Chat Log",
        data=chat_log_str,
        file_name="chat_log.json",
        mime="application/json",
    )