from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableSequence


class InputAnalysisChain:
    """ユーザーの入力が天気に関する質問かどうかを判定するクラス"""

    def __init__(self):
        prompt = ChatPromptTemplate.from_template(
            "与えられた質問が天気に関する質問かどうかを判定してください"
            "'weather'か'other'かのみ回答してください\n\nQuestion: {question}"
        )
        model = ChatOpenAI(temperature=0)
        output_parser = StrOutputParser()

        self.chain = prompt | model | output_parser

    async def analyze(self, user_input: str) -> str:
        return await self.chain.ainvoke("question", user_input)
