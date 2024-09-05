import os
import qdrant_client
from qdrant_client.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
import uuid

import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

#QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_HOST = "http://localhost"

PORT = 6333

COLLECTION_NAME = "weather_information_collections"


# TODO Chainにする
def load_qdrant():
    embeddings_model = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_API_BASE
    )

    client = qdrant_client.QdrantClient(url=f"{QDRANT_HOST}", port=PORT)

    collections = client.get_collections().collections
    collection_name = [collection.name for collection in collections]

    if COLLECTION_NAME not in collection_name:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print("Collection created")

    return Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings_model,
    )


def build_vector_store(docs_text, metadatas):
    qdrant = load_qdrant()
    qdrant.add_texts(texts=docs_text, metadatas=metadatas)


def read_files_with_metadata(directory):
    texts = []
    metadatas = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=20)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        doc_id = str(uuid.uuid4())
        metadata = {"DocumentID": doc_id, "source": filepath}

        # テキストファイルの処理
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()
                chunks = splitter.split_text(text)
                texts.extend(chunks)
                metadatas.extend(
                    [metadata] * len(chunks)
                )  # 各チャンクにメタデータを対応させる

        # PDFファイルの処理
        elif filename.endswith(".pdf"):
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                chunks = splitter.split_text(text)
                texts.extend(chunks)
                metadatas.extend(
                    [metadata] * len(chunks)
                )  # 各チャンクにメタデータを対応させる

    return texts, metadatas


if __name__ == "__main__":
    directory_path = os.path.join(
        os.getcwd(), "folder_name"
    )  # 参照するドキュメントが置いてあるフォルダ名の指定
    docs_texts, metadatas = read_files_with_metadata(directory_path)

    # テキストをQdrantDBに保存
    build_vector_store(docs_texts, metadatas)
    print("Documents with metadata have been added to Qdrant.")
