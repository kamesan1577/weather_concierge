import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

from .chains.main_chain import MainChain

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
        background_tasks.add_task(
            handler.handle, body.decode("utf-8"), x_line_signature
        )
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "ok"


@handler.add(MessageEvent)
def handle_message(event):
    if event.type != "message" or event.message.type != "text":
        return

    async def process_and_reply():
        try:
            result = await main_chain.process_query(event.message.text)
            message = result.get(
                "final_answer", "申し訳ありません。回答を生成できませんでした。"
            )
        except Exception as e:
            message = "申し訳ありません。エラーが発生しました。"
            print(e)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    background_tasks = BackgroundTasks()
    background_tasks.add_task(process_and_reply)

    return "ok"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
