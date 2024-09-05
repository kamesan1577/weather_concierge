from langchain.schema.runnable import RunnableSequence, RunnableBranch
from weather_concierge.chains.input_analysis_chain import InputAnalysisChain
from weather_concierge.chains.vector_db_lookup_chain import VectorDBLookupChain
from weather_concierge.chains.weather_api_chain import WeatherAPIChain
from weather_concierge.chains.response_generation_chain import ResponseGenerationChain

from weather_concierge.chains.models import *


class MainChain:
    """質問を受けてから回答までの処理の流れを定義するクラス(要はエントリーポイント)"""

    def __init__(self):
        self.question_analysis_chain = InputAnalysisChain()
        # self.weather_api_chain = WeatherAPIChain()
        self.vector_db_lookup_chain = VectorDBLookupChain()
        self.response_generation_chain = ResponseGenerationChain()

        self.full_chain = self.question_analysis_chain.analyze | RunnableBranch(
            (lambda x: x.category == "weather", self._weather_chain),
            (lambda x: x.category == "other", self._general_chain),
            self._default_chain,
        )

    async def _weather_chain(self, prompt: PromptModel) -> PromptModel:
        data = PromptModel(question=prompt.question)
        search_result = await self.vector_db_lookup_chain.search(data)
        response = await self.response_generation_chain.generate_response(search_result)

        return response

    def _general_chain(self, prompt: PromptModel) -> PromptModel:
        # return self.response_generation_chain.generate_response()
        return PromptModel(response="other")  # FIXME 仮置き

    def _default_chain(self, _):
        return PromptModel(response="other")  # FIXME 仮置き

    async def process_query(self, user_question: str) -> FinalAnswerModel:
        analysis_result = await self.question_analysis_chain.analyze(user_question)

        result = await self.full_chain.ainvoke(analysis_result)
        return FinalAnswerModel(final_answer=result.response)
