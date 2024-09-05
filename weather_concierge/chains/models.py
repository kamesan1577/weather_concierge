from pydantic import BaseModel


class PromptModel(BaseModel):
    question: str = ""  # ユーザーからの質問
    response: str = ""  # LLMからのレスポンス
    api_response: str = ""  # APIからのレスポンス
    context: str = ""  # RAGのコンテキスト
    category: str = ""  # 質問のカテゴリ


class FinalAnswerModel(BaseModel):
    final_answer: str
