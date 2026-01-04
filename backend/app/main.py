from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
from app.advisor.advisor import advise_action

app = FastAPI(title="Poker Advisor API")

class InputPayload(BaseModel):
    hand: List[str]
    board: List[str] = []
    position: str
    stack: float
    pot: float
    opponent_style: str
    action_history: List[str] = []
    mode: str = "beginner"

@app.post("/api/advise")
async def advise(payload: InputPayload) -> Any:
    try:
        result = advise_action(payload.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
