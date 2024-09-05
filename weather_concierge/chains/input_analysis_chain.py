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
            "与えられた質問が天気に関する質問かどうかを判定してください\n\n"
            "気象情報や自然現象などのキーワードが含まれる場合なども天気に関する質問として扱ってください\n\n"
            "'weather'か'other'かのみ回答してください\n\nQuestion: {question}"
        )

        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.environ["OPENAI_API_BASE"],
        )
        output_parser = StrOutputParser()
        self.chain = prompt | model | output_parser

    async def analyze(self, question: str, skip=False) -> PromptModel:
        if skip:
            return PromptModel(question=question, category="weather")
        print("analyze question: ", question)
        if isinstance(question, PromptModel):
            question = question.question
        category = await self.chain.ainvoke(input=question)
        return PromptModel(question=question, category=category)
