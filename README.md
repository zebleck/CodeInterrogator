# Streamlit Query Engine with Llama Index and GPT-4
## Introduction
This project is a Streamlit app that serves as a question-answering system using Llama Index and OpenAI's GPT-4. The application allows users to ask questions and retrieve accurate and relevant answers from a database of documents. This can be especially useful for searching through technical documentation, academic papers, or any structured set of documents. Also includes python scripts for scraping and cleaning online documentations.

## Features
* Interactive Query Interface: A user-friendly chat interface for queries.
* Customizable Response Modes: Choose how you would like the Llama Index to process and present your search results.
* Index Persistence: Load and save Llama Indices for quicker future queries.
* GPT-4 Assisted: Utilizes OpenAI's GPT-4 model for generating queries.

| :warning:   | Using an OpenAI model for document embedding and querying may incur significant costs. |
|---------------|:-------------------------|

## Installation
### Dependencies
To install the required Python packages, run the following command:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### API Keys

Create a `secrets.toml` file in the root directory with the following contents:

```
openai_key = "<Your OpenAI API key here>"
```

### Folder Structure

Ensure that your folder containing the data to be indexed is correctly placed. You can specify the folder path as a command-line argument.

## Usage

To run the Streamlit app, use the following command:

```
streamlit run <your_script_name.py> [folder_path]
```

Where `folder_path` is the path to the folder containing your documents. If `folder_path` is not specified, the default path './results' will be used.

### Customizing Query Response Modes

You can select from different response modes like "refine," "compact," "tree_summarize," etc., to customize how the information is retrieved and displayed.

## Contributing 

Feel free to submit pull requests or issues to improve the app.

## License

This project is licensed under the MIT License.
