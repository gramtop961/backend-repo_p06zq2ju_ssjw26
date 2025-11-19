"""
Database Schemas for TeleBuddy

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
Example: class Bot -> collection "bot"

These schemas are returned via GET /schema for the built-in DB viewer.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Any


class Bot(BaseModel):
    name: str = Field(..., description="Display name for this bot")
    username: Optional[str] = Field(None, description="Telegram @username of the bot")
    token: Optional[str] = Field(None, description="Telegram Bot API token (stored encrypted in production)")
    team_id: Optional[str] = Field(None, description="Team/Workspace this bot belongs to")
    welcome_message: Optional[str] = Field(None, description="Auto DM for join requests to private groups/channels")
    is_active: bool = Field(default=True, description="Whether bot is currently active")


class Fan(BaseModel):
    bot_id: str = Field(..., description="Bot this fan is associated with")
    tg_user_id: str = Field(..., description="Telegram user id")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    timezone: Optional[str] = Field(None, description="IANA timezone string if known")
    total_spend: float = Field(0, description="Total Stars revenue associated with this fan")


class MediaItem(BaseModel):
    bot_id: str = Field(..., description="Bot that owns this media item")
    type: Literal["photo", "video", "document"] = Field(..., description="Telegram media type")
    caption: Optional[str] = Field(None, description="Default caption to send with media")
    price: Optional[float] = Field(None, ge=0, description="Price in Stars or currency equivalent")
    external_url: Optional[str] = Field(None, description="External URL to fetch the file from (for demos)")
    telegram_file_id: Optional[str] = Field(None, description="Telegram file_id for instant reuse")
    tags: List[str] = Field(default_factory=list, description="Tags for quick filtering")
    thumbnail_url: Optional[str] = Field(None, description="Optional thumbnail url")


class ScriptStep(BaseModel):
    media_item_id: Optional[str] = Field(None, description="Reference to a media item")
    caption: Optional[str] = Field(None, description="Override caption for this step")
    price: Optional[float] = Field(None, description="Override price for this step")
    delay_minutes: int = Field(0, ge=0, description="Delay before sending this step in minutes")


class Script(BaseModel):
    bot_id: str = Field(..., description="Owning bot")
    name: str = Field(..., description="Name of the sales script")
    steps: List[ScriptStep] = Field(default_factory=list, description="Sequence of steps")


class Conversation(BaseModel):
    bot_id: str = Field(..., description="Owning bot")
    fan_id: str = Field(..., description="Fan in this conversation")
    last_message_preview: Optional[str] = Field(None, description="Preview text for list view")
    last_message_at: Optional[str] = Field(None, description="ISO time of last message")
    unread: int = Field(0, description="Unread count for agent side")


class Message(BaseModel):
    conversation_id: str = Field(..., description="Conversation this message belongs to")
    direction: Literal["inbound", "outbound"] = Field(..., description="Message direction")
    text: Optional[str] = Field(None, description="Text body")
    media_item_id: Optional[str] = Field(None, description="If message sent a media item")
    price: Optional[float] = Field(None, description="Price charged for paid media")
    paid: bool = Field(False, description="Whether this was paid content")
    telegram_message_id: Optional[int] = Field(None, description="Telegram message id if delivered")
    telegram_file_id: Optional[str] = Field(None, description="file_id used for instant delivery if any")


class Team(BaseModel):
    name: str = Field(..., description="Team name")


class TeamMember(BaseModel):
    team_id: str
    user_id: str
    role: Literal["owner", "admin", "agent", "viewer"] = "agent"


class AnalyticsDaily(BaseModel):
    bot_id: str
    date: str = Field(..., description="YYYY-MM-DD")
    revenue: float = 0
    paid_messages: int = 0
    unique_fans: int = 0


# Export model list for /schema endpoint convenience
ALL_MODELS: Dict[str, Any] = {
    "Bot": Bot,
    "Fan": Fan,
    "MediaItem": MediaItem,
    "ScriptStep": ScriptStep,
    "Script": Script,
    "Conversation": Conversation,
    "Message": Message,
    "Team": Team,
    "TeamMember": TeamMember,
    "AnalyticsDaily": AnalyticsDaily,
}
