import os
import asyncio
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

from weather_concierge.chains.main_chain import MainChain

app = FastAPI()
load_dotenv()
try:
    line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
    handler = WebhookHandler(os.environ["CHANNEL_SECRET"])
except KeyError as e:
    print(f"環境変数が設定されていません。{e}")
    raise


main_chain = MainChain()


@app.get("/")
def api_root():
    return {"message": "LINEBOT-API is running."}


@app.post("/callback")
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature=Header(None),
    summary="LINE Message APIからのコールバック",
):
    body = await request.body()
    try:
        handler.handle(body.decode(), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "ok"


@handler.add(MessageEvent)
def handle_message(event):
    asyncio.create_task(process_message(event))


async def process_message(event):
    print(event)
    if event.type != "message" or event.message.type != "text":
        print("Message type is not text")
        return

    try:
        result = await main_chain.process_query(event.message.text)
        message = result.get(
            "final_answer", "申し訳ありません。回答を生成できませんでした。"
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        message = "申し訳ありません。エラーが発生しました。"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        print(f"Reply sent: {message}")
    except Exception as e:
        print(f"Error sending reply: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
