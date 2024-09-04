from langchain.schema.runnable import RunnableSequence, RunnableBranch
from weather_concierge.chains.input_analysis_chain import InputAnalysisChain
from weather_concierge.chains.vector_db_lookup_chain import VectorDBLookupChain
from weather_concierge.chains.weather_api_chain import WeatherAPIChain
from weather_concierge.chains.response_generation_chain import ResponseGenerationChain


class MainChain:
    """質問を受けてから回答までの処理の流れを定義するクラス"""

    def __init__(self):
        # self.question_analysis_chain = InputAnalysisChain()
        # self.weather_api_chain = WeatherAPIChain()
        # self.response_generation_chain = ResponseGenerationChain()

        self.full_chain = RunnableSequence(
            [
                # self.question_analysis_chain,
                RunnableBranch(
                    (lambda x: x == "weather", self._weather_chain()),
                    (lambda x: x == "other", self._general_chain()),
                ),
            ]
        )

    def _weather_chain(self):
        pass  # あとで書く
        # return RunnableSequence(
        #     # DBを叩く
        #     # APIを叩く
        # )

    def _general_chain(self):
        pass
        # return self.response_generation_chain.generate_response()

    async def process_query(self, user_question: str) -> dict:
        result = await self.full_chain.ainvoke(user_question)
        return {"final_answer": result}
