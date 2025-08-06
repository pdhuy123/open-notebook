# Phiên bản mới (>=2.0)
from mindsdb_sdk import SDK

# Kết nối tới MindsDB
server = SDK('http://127.0.0.1:47334')  # Localhost
# Hoặc: server = SDK(login='email', password='password')  # Cloud

# Tạo Knowledge Base
config = {
    "name": "product_docs",
    "embedding_model": {
        "provider": "huggingface",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "storage": "chromadb",
    "data_source": {
        "file": "file_test"
    },
    "embedding_column": "content"
}

server.knowledge_bases.create(config)