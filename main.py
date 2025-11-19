import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import ALL_MODELS, MediaItem, Message, Conversation, Bot

app = FastAPI(title="TeleBuddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "TeleBuddy backend running"}


@app.get("/schema")
def get_schema():
    # Return available Pydantic schemas for the DB viewer tools
    return {name: model.model_json_schema() for name, model in ALL_MODELS.items()}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Simple seed endpoints for demo: list/create media items and conversations
class CreateMediaRequest(BaseModel):
    bot_id: str
    type: str
    caption: Optional[str] = None
    price: Optional[float] = None
    external_url: Optional[str] = None


@app.get("/api/media", response_model=List[dict])
def list_media(bot_id: Optional[str] = None, limit: int = 50):
    filter_q = {"bot_id": bot_id} if bot_id else {}
    items = get_documents("mediaitem", filter_q, limit)
    # Convert ObjectId to str
    for it in items:
        it["_id"] = str(it["_id"])
    return items


@app.post("/api/media")
def create_media(payload: CreateMediaRequest):
    doc = MediaItem(**payload.model_dump())
    inserted_id = create_document("mediaitem", doc)
    return {"id": inserted_id}


class CreateConversationRequest(BaseModel):
    bot_id: str
    fan_id: str
    last_message_preview: Optional[str] = None


@app.get("/api/conversations", response_model=List[dict])
def list_conversations(bot_id: str, limit: int = 50):
    items = get_documents("conversation", {"bot_id": bot_id}, limit)
    for it in items:
        it["_id"] = str(it["_id"])
    return items


@app.post("/api/conversations")
def create_conversation(payload: CreateConversationRequest):
    doc = Conversation(**payload.model_dump())
    inserted_id = create_document("conversation", doc)
    return {"id": inserted_id}


class SendMessageRequest(BaseModel):
    conversation_id: str
    text: Optional[str] = None
    media_item_id: Optional[str] = None
    paid: bool = False
    price: Optional[float] = None


@app.get("/api/messages", response_model=List[dict])
def list_messages(conversation_id: str, limit: int = 100):
    items = get_documents("message", {"conversation_id": conversation_id}, limit)
    for it in items:
        it["_id"] = str(it["_id"])
    return items


@app.post("/api/messages")
def send_message(payload: SendMessageRequest):
    # In a real integration, we would call Telegram here.
    # For this demo, we store the message and mimic an instant telegram_message_id.
    msg = Message(
        conversation_id=payload.conversation_id,
        direction="outbound",
        text=payload.text,
        media_item_id=payload.media_item_id,
        paid=payload.paid,
        price=payload.price,
        telegram_message_id=123456  # demo placeholder
    )
    inserted_id = create_document("message", msg)
    return {"id": inserted_id, "telegram_message_id": msg.telegram_message_id}


# Minimal bot management for multi-bot tab bar
class CreateBotRequest(BaseModel):
    name: str
    username: Optional[str] = None


@app.get("/api/bots", response_model=List[dict])
def list_bots(limit: int = 20):
    items = get_documents("bot", {}, limit)
    for it in items:
        it["_id"] = str(it["_id"])
    return items


@app.post("/api/bots")
def create_bot(payload: CreateBotRequest):
    bot = Bot(name=payload.name, username=payload.username)
    inserted_id = create_document("bot", bot)
    return {"id": inserted_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
