from langchain_openai import OpenAIEmbeddings
from langchain.schema.runnable import RunnableSequence

from weather_concierge.chains.models import PromptModel


class VectorDBLookupChain:
    """VectorDBから質問に関連する情報を取得するチェーン"""

    def __init__(self):
        pass  # あとで書く

    async def search(
        self, Prompt: PromptModel
    ) -> PromptModel:  # TODO ここのプロトタイプは仮
        """質問を受け取って、VectorDBから関連する気象情報を取得し、返す

        Args:
            Prompt (PromptModel): 質問内容

        Returns:
            PromptModel: VectorDBから取得した気象情報のチャンク
        """
        return
