import streamlit as st
import os
import sys
import logging
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, get_response_synthesizer, load_index_from_storage, ServiceContext
from llama_index.indices.document_summary import DocumentSummaryIndex, DocumentSummaryIndexRetriever
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
import openai
import json
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

# Initialize session state
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": f"Ask me a question about {index_name}'s document base!"}
    ]

    
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
		logging.info(f"Could not load index: {e}\nCreating index...")
		documents = SimpleDirectoryReader(folder_path, recursive=True).load_data()
		service_context = ServiceContext.from_defaults(llm=OpenAI(temperature=0, model="gpt-3.5-turbo"), chunk_size=1024)#, temperature=0.5, system_prompt="You are an expert on the LLama index Python library and your job is to answer technical questions. Assume that all questions are related to the LLama index Python library. Keep your answers technical and based on facts – do not hallucinate features."))

		#index = VectorStoreIndex.from_documents(documents, service_context=service_context)
		response_synthesizer = get_response_synthesizer(
			response_mode="tree_summarize", use_async=True
		)
		index = DocumentSummaryIndex.from_documents(
			documents,
			service_context=service_context,
			response_synthesizer=response_synthesizer,
		)
		index.set_index_id(index_name)
		index.storage_context.persist(f"./storage/{index_name}")
		logging.info(f"Created index: {index}")
		return index

index = load_data()

# Define chat engine
#mode = st.selectbox("Select query mode", ["condense_question", "best", "context", "simple", "react", "openai"])
#chat_engine = index.as_chat_engine(chat_mode=mode, verbose=True)

response_mode = st.selectbox("Select response mode", ["refine", "compact", "tree_summarize", "simple_summarize", "no_text", "accumulate", "compact_accumulate"])

choice_batch_size = st.number_input('Select the number of similar nodes to retrieve', min_value=1, max_value=100, value=1)

#query_engine = index.as_query_engine(response_mode=response_mode)#, similarity_top_k=similarity_top_k, verbose=True)
retriever = DocumentSummaryIndexRetriever(index, choice_batch_size, response_mode=response_mode, verbose=True)

response_synthesizer = get_response_synthesizer()

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer
)

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
			logging.info(prompt)
			response = query_engine.query(prompt)
			#response = retriever.retrieve(prompt)
			#print(response)
			#for i, r in enumerate(response):
			#	st.write(f"#{i+1}<br>{r.node.get_text()}")
			#	st.session_state.messages.append({"role": "assistant", "content": r.node.get_text()})
			# if is error
			logging.warn(response)
			st.write(f"{response.response}")
			logging.info(response)
			st.session_state.messages.append({"role": "assistant", "content": response.response})

# Button to export chat log
if st.button('Export Chat Log'):
    chat_log_str = json.dumps(st.session_state.messages, indent=4)
    st.download_button(
        label="Download Chat Log",
        data=chat_log_str,
        file_name="chat_log.json",
        mime="application/json",
    )