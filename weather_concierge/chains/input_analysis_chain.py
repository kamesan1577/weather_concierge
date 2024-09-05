import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableSequence
from weather_concierge.chains.models import PromptModel
from dotenv import load_dotenv


class InputAnalysisChain:
    """ユーザーの入力が天気に関する質問かどうかを判定するチェーン"""

    def __init__(self):
        load_dotenv()
        prompt = ChatPromptTemplate.from_template(
            "与えられた質問が天気に関する質問かどうかを判定してください"
            "'weather'か'other'かのみ回答してください\n\nQuestion: {question}"
        )

        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.environ["OPENAI_API_BASE"],
        )
        output_parser = StrOutputParser()

        self.chain = prompt | model | output_parser

    async def analyze(self, question: str) -> PromptModel:
        if isinstance(question, PromptModel):
            question = question.question
        category = await self.chain.ainvoke(input=question)
        return PromptModel(question=question, category=category)
