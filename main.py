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
import nest_asyncio
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import ServiceContext, set_global_service_context
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding, HuggingFaceEmbedding
from llama_index.node_parser import SentenceWindowNodeParser
from llama_index.indices.postprocessor import MetadataReplacementPostProcessor

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
		logging.info(f"Could not load index: {e}")

		node_parser = SentenceWindowNodeParser.from_defaults(
			window_size=3,
			window_metadata_key="window",
			original_text_metadata_key="original_text",
		)
		llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
		ctx = ServiceContext.from_defaults(
			llm=llm,
			embed_model=OpenAIEmbedding(embed_batch_size=5),
            node_parser=node_parser
		)
		logging.info(f"Loading documents.")
		documents = SimpleDirectoryReader(folder_path, recursive=True).load_data()
		logging.info(f"Creating index.")
		sentence_index = VectorStoreIndex.from_documents(documents, service_context=ctx)

		sentence_index.set_index_id(index_name)
		sentence_index.storage_context.persist(f"./storage/{index_name}")
		logging.info(f"Created index: {sentence_index}")
		return sentence_index

index = load_data()

similarity_top_k = st.number_input('Select the number of similar nodes to retrieve', min_value=1, max_value=100, value=2)

query_engine = index.as_query_engine(
    similarity_top_k=similarity_top_k,
    # the target key defaults to `window` to match the node_parser's default
    node_postprocessors=[
        MetadataReplacementPostProcessor(target_metadata_key="window")
    ],
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
			for i, source_node in enumerate(response.source_nodes):
				if i == 0:
					print(source_node)
				st.write(i, "\n", source_node.node.metadata["original_text"])
			st.write(f"{response.response}")
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