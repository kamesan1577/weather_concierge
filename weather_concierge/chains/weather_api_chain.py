from langchain.schema.runnable import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import (
    AgentExecutor,
    tool,
    create_tool_calling_agent,
    Tool,
)
from langchain_core.tools import StructuredTool
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
import urllib.request
import re
from bs4 import BeautifulSoup as bs
from weather_concierge.chains.models import PromptModel

CLASS_AREA_CODE = "1310100"  # 市町村区のコード
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
# WARNING_INFO_URL = (
#     "https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=%s&lang=ja"
# )
WARNING_INFO_URL = "https://www.jma.go.jp/bosai/warning/#area_type=class20s&lang=ja"
WARNING_DATA_URL = "https://www.jma.go.jp/bosai/warning/data/warning/%s.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/%s.json"


@tool
def get_warning_info():
    """各地の警報・注意報の情報を取得する"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    req = urllib.request.Request(WARNING_INFO_URL, headers=headers)
    with urllib.request.urlopen(req) as res:
        print(res.getcode())
        warnings_soup = bs(res.read(), "html.parser")

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
    return {"warning_texts": warning_texts, "area": area}


class ForecastInput(BaseModel):
    area_code: str = Field(..., description="地域コード(東京の場合は'130000')")


def get_forecast_data(area_code: str):
    """天気予報を取得する

    Args:
        area_code: 地域コード(東京の場合は"130000")

    Returns:
        dict: 天気予報データ
    """
    forecast_url = FORECAST_URL % area_code
    forecast_data = urllib.request.urlopen(forecast_url)
    forecast_data = json.loads(forecast_data.read())
    return forecast_data


class WeatherAPIChain:
    """APIと連携し、プロンプトに基づいて適切な天気情報を取得するチェーン"""

    def __init__(self):
        load_dotenv()
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.environ["OPENAI_API_BASE"],
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            以下の質問に対して、適切な天気情報APIを選択し、その結果を解釈してください:

            利用可能なAPI:
            1. 警報情報API (get_warning_info)
            2. 天気予報API (get_forecast_data)
            選択したAPIの結果を解釈し、簡単なサマリーを出力してください。

            注意: get_forecast_data を使用する場合は、適切な地域コードを指定してください。東京の場合は "130000" です。
            """,
                ),
                (
                    "user",
                    """
            質問: {question}
            関連資料: {context}
            """,
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        forecast_tool = StructuredTool.from_function(
            func=get_forecast_data,
            name="get_forecast_data",
            description="天気予報を取得する",
            args_schema=ForecastInput,
        )
        tools = [
            Tool(
                name="get_warning_info",
                func=get_warning_info,
                description="警報情報を取得する",
            ),
            forecast_tool,
        ]
        agent = create_tool_calling_agent(
            llm=model,
            tools=tools,
            prompt=prompt_template,
        )

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        # self.chain = self.prompt_template | self.model | StrOutputParser()

    async def process(self, prompt: PromptModel) -> PromptModel:
        try:
            # # 警報情報を取得
            # warning_texts, area = get_warning_info()

            # # 天気予報情報を取得
            # forecast_data = get_forecast_data(CLASS_AREA_CODE)

            # LLMを使用してAPIレスポンスを解釈し、質問に答える
            # llm_summary = await self.chain.ainvoke(
            #     {"question": prompt.question, "context": prompt.context}
            # )
            llm_summary = await self.agent_executor.ainvoke(
                {
                    "question": prompt.question,
                    "context": prompt.context,
                }
            )
            print("llm_summary: ", llm_summary["output"])

            return PromptModel(
                question=prompt.question,
                api_response=llm_summary["output"],
                context=prompt.context,
            )
        except Exception as e:
            print(e)
            return PromptModel(
                question=prompt.question,
                api_response="error occurred",
            )
