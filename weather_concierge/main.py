from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    client = QdrantClient("qdrant", port=6333)
    client.recreate_collection(
        collection_name="my_collection",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/query")
def query_qdrant(q: str):
    client = QdrantClient("qdrant", port=6333)
    # ここにQdrantを使用したクエリロジックを実装します
    return {"query": q, "result": "Sample result"}