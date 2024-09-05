from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
from weather_concierge.chains.models import PromptModel


class VectorDBLookupChain:
    """VectorDBから質問に関連する情報を取得するチェーン"""

    def __init__(self):
        load_dotenv()
        # modelの指定。今回はGPT4 miniを採用
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.environ["OPENAI_API_BASE"],
        )

        # Embedding modelはOpenAIのものを利用
        embedding_function = OpenAIEmbeddings(
            base_url=os.environ["OPENAI_API_BASE"],
        )

        # ベクトルDBの設定。今回はEmbeddingに時間がかかるのであらかじめ用意したcollectionを利用

        qdrant_client = QdrantClient(host=os.environ["QDRANT_HOST"], port=6333)

        qdrant = QdrantVectorStore(
            client=qdrant_client,
            embedding=embedding_function,
            collection_name="weather_information_collections",
        )
        # retrieverの定義
        retriever = qdrant.as_retriever(
            search_type="mmr", k=10, verbose=True
        )  # ベクトル検索機能を設定

        description_prompt = ChatPromptTemplate.from_template("""
        マークダウン形式で返答してください。
        {context}の情報に基づいて、以下の質問に答えてください:
        {question}
        """)
        # チェーンの定義
        self.chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | description_prompt
            | model
            | StrOutputParser()
        )

    async def search(self, prompt: PromptModel) -> PromptModel:
        context = await self.chain.ainvoke(prompt.question)
        print("context: ", context)
        result = PromptModel(question=prompt.question, context=context)
        return result
