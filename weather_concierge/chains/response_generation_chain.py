import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableSequence
from weather_concierge.chains.models import PromptModel
from dotenv import load_dotenv


class ResponseGenerationChain:
    """質問内容と天気情報を受け取り、回答を生成するためのチェーン"""

    # input_analysis_chain.pyみたいな感じで書く
    def __init__(self):
        load_dotenv()
        prompt = ChatPromptTemplate.from_template(
            "あなたはプロの天気予報士です。以下の質問に答えてください。\n\nWeatherInfoやContextがある場合は参照してください\n\n"
            "Question: {question}\n\n WeatherInfo: {weather_info}\n\n Context: {context}"
        )
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_base_url=os.environ["OPENAI_API_BASE"],
        )
        output_parser = StrOutputParser()

        self.chain = prompt | model | output_parser

    async def generate_response(self, prompt: PromptModel) -> PromptModel:
        result = await self.chain.ainvoke(
            question=prompt.question,
            weather_info=prompt.api_response,
            context=prompt.context,
        )
        return result
