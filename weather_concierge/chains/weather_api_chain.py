# from langchain.api_chain import APIChain
from langchain_openai import OpenAI


class WeatherAPIChain:
    """VectorDBからの情報を元に適切なAPIと連携し、天気情報を取得するチェーン"""

    def __init__(self):
        pass  # ←中身書いたら消す

    async def get_weather_info(
        self, location: str
    ) -> dict:  # TODO ここのプロトタイプは仮
        return
