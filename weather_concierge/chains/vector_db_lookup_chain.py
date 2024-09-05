from langchain_openai import OpenAIEmbeddings
from langchain.schema.runnable import RunnableSequence
import json
from fastapi import FastAPI, APIRouter, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

# from langserve import add_routes
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent

# from langchain_experimental.tools import PythonREPLTool
import os
from typing import AsyncIterable, Dict
from langchain.load import dumps, loads

from weather_concierge.chains.models import PromptModel


class VectorDBLookupChain:
    """VectorDBから質問に関連する情報を取得するチェーン"""

    def __init__(self):
        pass  # あとで書く

    async def search(
        self,
    ) -> dict:  # TODO ここのプロトタイプは仮
        return  # あとで書く

    def rag(self, question):
        # modelの指定。今回はGPT4 miniを採用
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            streaming=True,
            openai_api_base="https://api.openai.iniad.org/api/v1/",
        )

        # Embedding modelはOpenAIのものを利用
        embedding_function = OpenAIEmbeddings(
            openai_api_base="https://api.openai.iniad.org/api/v1/"
        )

        # ベクトルDBの設定。今回はEmbeddingに時間がかかるのであらかじめ用意したcollectionを利用

        qdrant_client = QdrantClient(host="localhost", port=6333)
        qdrant = Qdrant(
            client=qdrant_client,
            embeddings=embedding_function,
            collection_name="aws_documents",
        )
        # retrieverの定義
        retriever = qdrant.as_retriever(
            search_type="mmr", k=10, verbose=True
        )  # ベクトル検索機能を設定

        # ユーザからの入力に応じて、サービス設計を返すプロンプト
        description_prompt = ChatPromptTemplate.from_template("""
        マークダウン形式で返答してください。
        {input}に関連する情報をください。
        """)
        # チェーンの定義
        description_chain = description_prompt | model | StrOutputParser()

        # チェーンの動作イメージ
        return description_chain.invoke({"input": question})
