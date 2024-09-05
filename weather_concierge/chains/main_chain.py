from langchain.schema.runnable import RunnableSequence, RunnableBranch
from weather_concierge.chains.input_analysis_chain import InputAnalysisChain
from weather_concierge.chains.vector_db_lookup_chain import VectorDBLookupChain
from weather_concierge.chains.weather_api_chain import WeatherAPIChain
from weather_concierge.chains.response_generation_chain import ResponseGenerationChain


class MainChain:
    """質問を受けてから回答までの処理の流れを定義するクラス(要はエントリーポイント)"""

    def __init__(self):
        # self.question_analysis_chain = InputAnalysisChain()
        # self.weather_api_chain = WeatherAPIChain()
        # self.vector_db_lookup_chain = VectorDBLookupChain()
        # self.response_generation_chain = ResponseGenerationChain()

        self.full_chain = self._dummy_analysis_chain | RunnableBranch(
            (lambda x: x["category"] == "weather", self._weather_chain),
            (lambda x: x["category"] == "other", self._general_chain),
            self._default_chain,
        )

    def _dummy_analysis_chain(self, question: dict) -> dict:
        # FIXME question_analysis_chainを実装したら消す
        return {"category": "weather"}  # 辞書を返す

    def _weather_chain(self, _):
        # return RunnableSequence(
        #     # DBを叩く
        #     # APIを叩く
        # )
        return {"response": "weather"}  # FIXME 仮置き

    def _general_chain(self, _):
        # return self.response_generation_chain.generate_response()
        return {"response": "other"}  # FIXME 仮置き

    def _default_chain(self, _):
        return {"response": "default"}

    async def process_query(self, user_question: str) -> dict:
        result = await self.full_chain.ainvoke({"question": user_question})
        return {"final_answer": result["response"]}
