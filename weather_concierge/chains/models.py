from pydantic import BaseModel


class AnalysisResultModel(BaseModel):
    category: str


class PromptModel(BaseModel):
    question: str = ""  # ユーザーからの質問
    response: str = ""  # LLMからのレスポンス
    api_response: str = ""  # APIからのレスポンス
    context: str = ""  # RAGのコンテキスト


class FinalAnswerModel(BaseModel):
    final_answer: str
