"""Pydantic v2 request and response schemas.

Every field uses Field() with description and example values.
Every model includes json_schema_extra for OpenAPI documentation.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import RiskLevel


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    session_id: str | None = Field(
        default=None,
        description="Existing session ID to continue a conversation. Omit to create a new session.",
        examples=["sess_a1b2c3d4"],
    )
    user_message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message text. Must be between 1 and 2000 characters.",
        examples=["I've been feeling stressed lately"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": None,
                    "user_message": "I've been feeling stressed lately",
                }
            ]
        }
    }


class CrisisResource(BaseModel):
    """Emergency mental health resource for Mexico."""

    name: str = Field(
        description="Name of the crisis service.",
        examples=["Linea de la Vida"],
    )
    number: str = Field(
        description="Phone number to call.",
        examples=["800-911-2000"],
    )
    hours: str = Field(
        description="Hours of availability.",
        examples=["24/7"],
    )
    type: str = Field(
        description="Type of service provided.",
        examples=["hotline"],
    )
    description: str = Field(
        description="Brief description of the service.",
        examples=["Free national crisis hotline"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Linea de la Vida",
                    "number": "800-911-2000",
                    "hours": "24/7",
                    "type": "hotline",
                    "description": "Free national crisis hotline",
                }
            ]
        }
    }


class MessageEntry(BaseModel):
    """Single message in a conversation history."""

    role: str = Field(
        description="Message author role: user, assistant, or system.",
        examples=["user"],
    )
    content: str = Field(
        description="Message text content.",
        examples=["I've been feeling overwhelmed at work"],
    )
    risk_score: int | None = Field(
        default=None,
        description="Risk score computed for this message (0-100). Only present for user messages.",
        examples=[25],
    )
    timestamp: datetime = Field(
        description="UTC timestamp when the message was recorded.",
        examples=["2024-01-15T10:30:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "I've been feeling overwhelmed at work",
                    "risk_score": 25,
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    session_id: str = Field(
        description="Session identifier for this conversation.",
        examples=["sess_a1b2c3d4"],
    )
    bot_response: str = Field(
        description="The chatbot's response text.",
        examples=["I hear you. It sounds like you've been carrying a lot."],
    )
    risk_score: int = Field(
        description="Computed risk score for the user's message (0-100).",
        ge=0,
        le=100,
        examples=[15],
    )
    risk_level: RiskLevel = Field(
        description="Risk classification derived from the score.",
        examples=["low"],
    )
    triage_activated: bool = Field(
        description="Whether triage evaluation was triggered.",
        examples=[False],
    )
    human_handoff: bool = Field(
        description="Whether the session is being handed off to a professional.",
        examples=[False],
    )
    crisis_resources: list[CrisisResource] | None = Field(
        default=None,
        description="Crisis resources provided when risk is critical.",
    )
    session_message_count: int = Field(
        description="Total number of messages in this session.",
        examples=[1],
    )
    timestamp: datetime = Field(
        description="UTC timestamp of this response.",
        examples=["2024-01-15T10:30:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "sess_a1b2c3d4",
                    "bot_response": "I hear you. It sounds like you've been carrying a lot.",
                    "risk_score": 15,
                    "risk_level": "low",
                    "triage_activated": False,
                    "human_handoff": False,
                    "crisis_resources": None,
                    "session_message_count": 1,
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class SessionHistoryResponse(BaseModel):
    """Full conversation history for a session."""

    session_id: str = Field(
        description="Session identifier.",
        examples=["sess_a1b2c3d4"],
    )
    history: list[MessageEntry] = Field(
        description="Ordered list of messages in the conversation.",
    )
    message_count: int = Field(
        description="Total number of messages in the session.",
        examples=[10],
    )
    cumulative_risk: int = Field(
        description="Sum of all risk scores in the session.",
        examples=[85],
    )
    triage_activated: bool = Field(
        description="Whether triage has been activated in this session.",
        examples=[False],
    )
    created_at: datetime = Field(
        description="UTC timestamp when the session was created.",
        examples=["2024-01-15T10:00:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "sess_a1b2c3d4",
                    "history": [],
                    "message_count": 0,
                    "cumulative_risk": 0,
                    "triage_activated": False,
                    "created_at": "2024-01-15T10:00:00Z",
                }
            ]
        }
    }


class HandoffResponse(BaseModel):
    """Response when a session is handed off to a professional."""

    session_id: str = Field(
        description="Session identifier being handed off.",
        examples=["sess_a1b2c3d4"],
    )
    handoff_status: str = Field(
        description="Current handoff status.",
        examples=["initiated"],
    )
    professional_context: dict = Field(
        description="Context summary provided to the incoming professional.",
        examples=[{"message_count": 5, "risk_level": "high"}],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "sess_a1b2c3d4",
                    "handoff_status": "initiated",
                    "professional_context": {
                        "message_count": 5,
                        "risk_level": "high",
                    },
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: str = Field(
        description="Service health status.",
        examples=["healthy"],
    )
    service: str = Field(
        description="Service name.",
        examples=["AI Clinical Chatbot MVP"],
    )
    version: str = Field(
        description="Service version.",
        examples=["0.1.0"],
    )
    active_sessions: int = Field(
        description="Number of currently active sessions.",
        examples=[3],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "service": "AI Clinical Chatbot MVP",
                    "version": "0.1.0",
                    "active_sessions": 3,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str = Field(
        description="Human-readable error description.",
        examples=["Session not found"],
    )
    error_code: str | None = Field(
        default=None,
        description="Machine-readable error code for client handling.",
        examples=["SESSION_NOT_FOUND"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Session not found",
                    "error_code": "SESSION_NOT_FOUND",
                }
            ]
        }
    }
