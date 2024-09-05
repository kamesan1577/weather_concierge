"""
# from langchain.api_chain import APIChain
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.mrkl import prompt




class WeatherAPIChain:
    #VectorDBからの情報を元に適切なAPIと連携し、天気情報を取得するチェーン

    def __init__(self, area, weathers, winds, warning, probability):
        self.area = area
        self.get_weathers = weathers
        self.winds = winds
        self.warning = warning
        self.probability = probability

    async def get_weather_info(
        self, location: str
    ) -> dict:  # TODO ここのプロトタイプは仮
        return
"""

from langchain.schema.runnable import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json
import urllib.request
import re
from bs4 import BeautifulSoup as bs
from weather_concierge.chains.models import PromptModel

CLASS_AREA_CODE = "1310100"  # 市町村区のコード
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
WARNING_INFO_URL = (
    "https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=%s&lang=ja"
    % (CLASS_AREA_CODE)
)
WARNING_DATA_URL = "https://www.jma.go.jp/bosai/warning/data/warning/%s.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/%s.json"


def get_warning_info():
    warnings_soup = bs(urllib.request.urlopen(WARNING_INFO_URL).read(), "html.parser")
    warnings_contents = warnings_soup.find_all("script")[10]
    warnings_text_list = str(warnings_contents).split("},")
    warnings_list = [
        re.findall(r"\w+", warning)
        for warning in warnings_text_list
        if ':{name1:"' in warning
    ]
    trans_warning = {}
    for warning_datas in warnings_list:
        warning_text = ""
        for warning_data in warning_datas:
            if warning_data in "elem":
                break
            if warning_data in ["c", "name1", "name2"]:
                continue
            if warning_data.isdecimal():
                warning_code = warning_data
                continue
            warning_text += "\\" + warning_data
        trans_warning[warning_code] = warning_text.encode("ascii").decode(
            "unicode-escape"
        )

    area_data = urllib.request.urlopen(url=AREA_URL)
    area_data = json.loads(area_data.read())
    area = area_data["class20s"][CLASS_AREA_CODE]["name"]
    class15s_area_code = area_data["class20s"][CLASS_AREA_CODE]["parent"]
    class10s_area_code = area_data["class15s"][class15s_area_code]["parent"]
    offices_area_code = area_data["class10s"][class10s_area_code]["parent"]
    warning_info = urllib.request.urlopen(
        url=WARNING_DATA_URL.format(offices_area_code)
    )
    warning_info = json.loads(warning_info.read())
    warning_codes = [
        warning["code"]
        for class_area in warning_info["areaTypes"][1]["areas"]
        if class_area["code"] == CLASS_AREA_CODE
        for warning in class_area["warnings"]
        if warning["status"] != "解除" and warning["status"] != "発表警報・注意報はなし"
    ]
    warning_texts = [trans_warning[code] for code in warning_codes]
    return (warning_texts, area)


def get_forecast_data(area_code):
    forecast_url = FORECAST_URL % area_code
    forecast_data = urllib.request.urlopen(forecast_url)
    forecast_data = json.loads(forecast_data.read())
    return forecast_data


class WeatherAPIChain:
    """APIと連携し、プロンプトに基づいて適切な天気情報を取得するチェーン"""

    def __init__(self):
        load_dotenv()
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            streaming=True,
            base_url=os.environ["OPENAI_API_BASE"],
        )

        self.prompt_template = ChatPromptTemplate.from_template("""
        以下の質問に対して、適切な天気情報APIを選択し、その結果を解釈してください:


        利用可能なAPI:
        1. 警報情報API (get_warning_info)
        2. 天気予報API (get_forecast_data)

        選択したAPIの結果を解釈し、簡単なサマリーを出力してください。

        質問: {question}
        関連資料: {context}
        """)

        self.chain = self.prompt_template | self.model | StrOutputParser()

    async def process(self, prompt: PromptModel) -> PromptModel:
        try:
            # 警報情報を取得
            warning_texts, area = get_warning_info()

            # 天気予報情報を取得
            forecast_data = get_forecast_data(CLASS_AREA_CODE)

            # LLMを使用してAPIレスポンスを解釈し、質問に答える
            llm_summary = await self.chain.ainvoke(
                {"question": prompt.question, "context": prompt.context}
            )

            # APIレスポンスを統合
            api_response = {
                "area": area,
                "warnings": warning_texts,
                "forecast": forecast_data,
                "llm_response": llm_summary,
            }

            print("API response: ", api_response)
            return PromptModel(
                question=prompt.question,
                api_response=json.dumps(api_response),
                context=prompt.context,
            )
        except Exception as e:
            print(e)
            return PromptModel(
                question=prompt.question,
                api_response="error occurred",
            )


# import json
# import urllib.request
# import re
# from bs4 import BeautifulSoup as bs
# import asyncio
# from langchain_openai import OpenAI
# from langchain.agents import initialize_agent, Tool
# from langchain.agents.mrkl import prompt

# CLASS_AREA_CODE = "1310100"  # 市町村区のコード
# AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
# WARNING_INFO_URL = "https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=%s&lang=ja" % (CLASS_AREA_CODE)
# WARNING_DATA_URL = "https://www.jma.go.jp/bosai/warning/data/warning/%s.json"
# FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/%s.json"

# def get_warning_info():
#     warnings_soup = bs(urllib.request.urlopen(WARNING_INFO_URL).read(), 'html.parser')
#     warnings_contents = warnings_soup.find_all('script')[10]
#     warnings_text_list = str(warnings_contents).split("},")
#     warnings_list = [re.findall(r'\w+', warning) for warning in warnings_text_list if ':{name1:"' in warning]
#     trans_warning = {}
#     for warning_datas in warnings_list:
#         warning_text = ''
#         for warning_data in warning_datas:
#             if warning_data in 'elem':
#                 break
#             if warning_data in ['c', 'name1', 'name2']:
#                 continue
#             if warning_data.isdecimal():
#                 warning_code = warning_data
#                 continue
#             warning_text += '\\' + warning_data
#         trans_warning[warning_code] = warning_text.encode('ascii').decode('unicode-escape')

#     area_data = urllib.request.urlopen(url=AREA_URL)
#     area_data = json.loads(area_data.read())
#     area = area_data["class20s"][CLASS_AREA_CODE]["name"]
#     class15s_area_code = area_data['class20s'][CLASS_AREA_CODE]['parent']
#     class10s_area_code = area_data['class15s'][class15s_area_code]['parent']
#     offices_area_code = area_data['class10s'][class10s_area_code]['parent']
#     warning_info = urllib.request.urlopen(url=WARNING_DATA_URL % (offices_area_code))
#     warning_info = json.loads(warning_info.read())
#     warning_codes = [warning["code"]
#                     for class_area in warning_info["areaTypes"][1]["areas"]
#                     if class_area["code"] == CLASS_AREA_CODE
#                     for warning in class_area["warnings"]
#                     if warning["status"] != "解除" and warning["status"] != "発表警報・注意報はなし"]
#     warning_texts = [trans_warning[code] for code in warning_codes]
#     return (warning_texts, area)

# def get_forecast_data(area_code):
#     forecast_url = FORECAST_URL % area_code
#     forecast_data = urllib.request.urlopen(forecast_url)
#     forecast_data = json.loads(forecast_data.read())
#     return forecast_data

# class WeatherAPIChain:
#     """VectorDBからの情報を元に適切なAPIと連携し、天気情報を取得するチェーン"""

#     def __init__(self, area_code):
#         self.area_code = area_code

#     async def get_weather_info(self) -> dict:
#         # 警報情報を取得
#         warning_texts, area = get_warning_info()

#         # 天気予報情報を取得
#         forecast_data = get_forecast_data(self.area_code)

#         # 必要な情報を統合して返す
#         weather_info = {
#             "area": area,
#             "forecast": forecast_data,
#             "warnings": warning_texts
#         }
#         return weather_info

# async def main():
#     weather_chain = WeatherAPIChain(area_code="130000")  # 適切なエリアコードを指定
#     weather_info = await weather_chain.get_weather_info()
#     print(weather_info)

# if __name__ == '__main__':
#     asyncio.run(main())
