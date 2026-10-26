from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import ask, tool_config, json_config, Answer

app = FastAPI()

# 📮 What the user sends in
class Question(BaseModel):
    question: str

# 🚪 The endpoint (the drive-thru window)
@app.post("/ask")
def ask_agent(q: Question) -> Answer:
    try:
        draft = ask(q.question, tool_config)
        result = ask("Put this into the form: " + draft.text, json_config)
        return result.parsed
    except RuntimeError:
        # 🪂 All models down → a friendly error, not a crash
        raise HTTPException(status_code=503, detail="AI is busy, try again soon")
