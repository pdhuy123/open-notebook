import os

import streamlit as st

import utils.logs as logs

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import fitz
from llama_index.core import Document
# This is not used but required by llama-index and must be set FIRST
os.environ["OPENAI_API_KEY"] = "sk-abc123"

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.vector_stores import SimpleVectorStore

###################################
#
# Setup Embedding Model
#
###################################


@st.cache_resource(show_spinner=False)
def setup_embedding_model(
    model: str,
):
    """
    Sets up an embedding model using the Hugging Face library.

    Args:
        model (str): The name of the embedding model to use.

    Returns:
        An instance of the HuggingFaceEmbedding class, configured with the specified model and device.

    Raises:
        ValueError: If the specified model is not a valid embedding model.

    Notes:
        The `device` parameter can be set to 'cpu' or 'cuda' to specify the device to use for the embedding computations. If 'cuda' is used and CUDA is available, the embedding model will be run on the GPU. Otherwise, it will be run on the CPU.
    """
    try:
        from torch import cuda
        device = "cpu" if not cuda.is_available() else "cuda"
    except:
        device = "cpu"
    finally:
        logs.log.info(f"Using {device} to generate embeddings")

    try:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model,
            device=device,
        )

        logs.log.info(f"Embedding model created successfully")
        
        return
    except Exception as err:
        print(f"Failed to setup the embedding model: {err}")


###################################
#
# Load Documents
#
###################################


def load_documents(data_dir: str):
    """
    Loads documents from a directory of files, with Japanese PDF support.

    Args:
        data_dir (str): Directory containing files to load.

    Returns:
        List[Document]: Loaded documents.
    """
    documents = []

    try:
        for entry in os.scandir(data_dir):
            if not entry.is_file():
                continue
            filepath = entry.path
            ext = os.path.splitext(filepath)[1].lower()
            text = ""

            if ext == ".pdf":
                # Try using unstructured for better PDF + Japanese support
                try:
                    from unstructured.partition.pdf import partition_pdf
                    elements = partition_pdf(
                        filename=filepath,
                        strategy="hi_res",
                        languages=["jpn"]
                    )
                    text = "\n\n".join(
                        el.text for el in elements if getattr(el, 'text', None)
                    )
                except ImportError:
                    doc = fitz.open(filepath)
                    text = "".join(page.get_text() for page in doc)
            elif ext == ".pptx":
                # Use unstructured for PPTX files
                try:
                    from unstructured.partition.pptx import partition_pptx
                    elements = partition_pptx(
                        filename=filepath,
                        strategy="hi_res",
                        languages=["jpn"]
                    )
                    text = "\n\n".join(
                        el.text for el in elements if getattr(el, 'text', None)
                    )
                except ImportError:
                    doc = fitz.open(filepath)
                    text = "".join(page.get_text() for page in doc)
            else:
                files = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
                documents = files.load_data(files)
                logs.log.info(f"Loaded {len(documents):,} documents from files")
                return documents

            if text:
                documents.append(Document(
                    text=text,
                    metadata={"file_name": os.path.basename(filepath)}
                ))

        logs.log.info(f"Loaded {len(documents):,} documents from '{data_dir}'")
        return documents

    except Exception as err:
        logs.log.error(f"Error loading documents: {err}")
        raise

    finally:
        # Clean up files
        for file in os.scandir(data_dir):
            if file.is_file() and not file.name.startswith(".gitkeep"):
                try:
                    os.remove(file.path)
                except Exception:
                    pass
        logs.log.info("Document loading complete; removed local file(s)")


###################################
#
# Create Document Index
#
###################################


@st.cache_resource(show_spinner=False)
def create_index(_documents):
    """
    Creates an index from the provided documents and service context.

    Args:
        documents (list[str]): A list of strings representing the content of the documents to be indexed.

    Returns:
        An instance of `VectorStoreIndex`, containing the indexed data.

    Raises:
        Exception: If there is an error creating the index.

    Notes:
        The `documents` parameter should be a list of strings representing the content of the documents to be indexed.
    """

    try:
        # vector_store = SimpleVectorStore()
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(
            documents=_documents, show_progress=True,
        )
        logs.log.info("Index created from loaded documents successfully")
        # logs.log.info("Index created and saved successfully")

        return index
    except Exception as err:
        logs.log.error(f"Index creation failed: {err}")
        raise Exception(f"Index creation failed: {err}")


###################################
#
# Create Query Engine
#
###################################


# @st.cache_resource(show_spinner=False)
def create_query_engine(_documents):
    """
    Creates a query engine from the provided documents and service context.

    Args:
        documents (list[str]): A list of strings representing the content of the documents to be indexed.

    Returns:
        An instance of `QueryEngine`, containing the indexed data and allowing for querying of the data using a variety of parameters.

    Raises:
        Exception: If there is an error creating the query engine.

    Notes:
        The `documents` parameter should be a list of strings representing the content of the documents to be indexed.

        This function uses the `create_index` function to create an index from the provided documents and service context, and then creates a query engine from the resulting index. The `query_engine` parameter is used to specify the parameters of the query engine, including the number of top-ranked items to return (`similarity_top_k`) and the response mode (`response_mode`).
    """
    try:
        if _documents:
            index = create_index(_documents)
        else:
            vectordb_path = st.session_state.get("vectordb_path", "./vectordb")
            if not os.path.exists(vectordb_path):
                raise Exception(f"VectorDB folder '{vectordb_path}' does not exist.")

            storage_context = StorageContext.from_defaults(persist_dir=vectordb_path)
            index = load_index_from_storage(storage_context)

        query_engine = index.as_query_engine(
            similarity_top_k=st.session_state["top_k"],
            response_mode=st.session_state["chat_mode"],
            streaming=True,
        )

        st.session_state["query_engine"] = query_engine

        logs.log.info("Query Engine created successfully")

        return query_engine
    except Exception as e:
        logs.log.error(f"Error when creating Query Engine: {e}")
        raise Exception(f"Error when creating Query Engine: {e}")