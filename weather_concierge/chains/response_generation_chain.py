from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableSequence


class ResponseGenerationChain:
    """質問内容と天気情報を受け取り、回答を生成するためのチェーン"""

    # input_analysis_chain.pyみたいな感じで書く
    def __init__(self):
        pass  # ←中身書いたら消す

    async def generate_response(self, user_question: str, weather_info: dict) -> str:
        pass  # ←中身書いたら消す
