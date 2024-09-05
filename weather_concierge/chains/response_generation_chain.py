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
            "返答はLINEのメッセージに適した形式で返してください。\n\n"
            "WeatherInfoは質問に関連したAPIのレスポンスです。適切に解釈して解答に利用してください。\nContextは質問に関連した情報です。そのまま利用するのではなく、自然な形で解答に組み込んでください。\n\n"
            "Question: {question}\n\n WeatherInfo: {weather_info}\n\n Context: {context}"
        )
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.environ["OPENAI_API_BASE"],
        )
        output_parser = StrOutputParser()

        self.chain = prompt | model | output_parser

    async def generate_response(self, prompt: PromptModel) -> PromptModel:
        result = await self.chain.ainvoke(
            input={
                "question": prompt.question,
                "weather_info": prompt.api_response,
                "context": prompt.context,
            },
            # question=prompt.question,
            # weather_info=prompt.api_response,
            # context=prompt.context,
        )
        result = PromptModel(question=prompt.question, response=result)
        return result
