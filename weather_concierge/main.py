import os
import asyncio
import requests
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
    """この関数にLINEに送る処理を書く"""
    print(event)
    if event.type != "message" or event.message.type != "text":
        print("Message type is not text")
        return
    start_loading(event.source.user_id, 5)

    # try:
    result = await main_chain.process_query(event.message.text)
    message = result.final_answer
    # except Exception as e:
    #     print(f"Error processing query: {e}")
    #     message = "申し訳ありません。エラーが発生しました。"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        print(f"Reply sent: {message}")
    except Exception as e:
        print(f"Error sending reply: {e}")


def start_loading(chat_id, loading_seconds):
    """LINEのローディングアニメーションを表示する"""
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['CHANNEL_ACCESS_TOKEN']}",
    }
    payload = {"chatId": chat_id, "loadingSeconds": loading_seconds}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 202:
        print(
            f"Error starting loading animation: {response.status_code}, {response.text}"
        )
    else:
        print("Loading animation started successfully")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
