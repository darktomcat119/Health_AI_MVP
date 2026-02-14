"""Chat endpoints including SSE streaming.

Handles the full chat pipeline: session management, risk scoring,
triage evaluation, LLM response generation, and real-time streaming.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import (
    get_chatbot_service,
    get_risk_scorer,
    get_session_service,
    get_triage_evaluator,
)
from app.exceptions import SessionExpiredException, SessionNotFoundException
from app.models.enums import MessageRole
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HandoffResponse,
    MessageEntry,
    SessionHistoryResponse,
)
from app.services.chatbot import ChatbotService
from app.services.risk_scorer import RiskScorer
from app.services.session_service import SessionService
from app.services.triage_evaluator import TriageEvaluator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Delay between streamed tokens for natural reading feel
STREAM_TOKEN_DELAY_SECONDS = 0.03


@router.post(
    "/",
    response_model=ChatResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Send a chat message",
    description="Process a user message through the full pipeline and return the response.",
)
async def send_message(
    request: ChatRequest,
    session_service: SessionService = Depends(get_session_service),
    risk_scorer: RiskScorer = Depends(get_risk_scorer),
    triage_evaluator: TriageEvaluator = Depends(get_triage_evaluator),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> ChatResponse:
    """Process a user message and return the bot response.

    Args:
        request: Chat request with session ID and message.
        session_service: Injected session service.
        risk_scorer: Injected risk scoring engine.
        triage_evaluator: Injected triage evaluator.
        chatbot: Injected chatbot service.

    Returns:
        ChatResponse with bot response and risk assessment.

    Raises:
        HTTPException: On session errors or processing failures.
    """
    try:
        session = session_service.get_or_create(request.session_id)

        risk_score = risk_scorer.compute(request.user_message, session)
        risk_level = risk_scorer.classify(risk_score)

        session = session_service.add_user_message(
            session, request.user_message, risk_score, risk_level,
        )

        triage = triage_evaluator.evaluate(
            request.user_message, risk_score, risk_level, session,
        )

        if triage.triage_activated:
            session_service.mark_triage_activated(session)
        if triage.human_handoff:
            session_service.mark_handoff(session)

        if triage.override_response:
            bot_response = triage.override_response
        else:
            bot_response = await chatbot.generate_response(request.user_message, session)

        session_service.add_bot_message(session, bot_response)

        crisis_resources_data = None
        if triage.crisis_resources:
            crisis_resources_data = triage.crisis_resources

        logger.info(
            "Chat processed: session_id=%s, risk_score=%d, risk_level=%s, "
            "triage=%s, handoff=%s",
            session.id, risk_score, risk_level.value,
            triage.triage_activated, triage.human_handoff,
        )

        return ChatResponse(
            session_id=session.id,
            bot_response=bot_response,
            risk_score=risk_score,
            risk_level=risk_level,
            triage_activated=triage.triage_activated,
            human_handoff=triage.human_handoff,
            crisis_resources=crisis_resources_data,
            session_message_count=session.message_count,
            timestamp=datetime.now(timezone.utc),
        )

    except SessionExpiredException as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    except SessionNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/stream",
    summary="Stream a chat response via SSE",
    description="Process a user message and stream the response word by word via Server-Sent Events.",
)
async def stream_message(
    request: ChatRequest,
    session_service: SessionService = Depends(get_session_service),
    risk_scorer: RiskScorer = Depends(get_risk_scorer),
    triage_evaluator: TriageEvaluator = Depends(get_triage_evaluator),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    """Stream a chat response via Server-Sent Events.

    SSE event types:
    - metadata: Session info, risk score, triage status
    - crisis: Crisis resources (when applicable)
    - token: Individual word of the response
    - done: Stream complete with message count

    Args:
        request: Chat request with session ID and message.
        session_service: Injected session service.
        risk_scorer: Injected risk scoring engine.
        triage_evaluator: Injected triage evaluator.
        chatbot: Injected chatbot service.

    Returns:
        StreamingResponse with SSE event stream.
    """
    session = session_service.get_or_create(request.session_id)

    risk_score = risk_scorer.compute(request.user_message, session)
    risk_level = risk_scorer.classify(risk_score)

    session = session_service.add_user_message(
        session, request.user_message, risk_score, risk_level,
    )

    triage = triage_evaluator.evaluate(
        request.user_message, risk_score, risk_level, session,
    )

    if triage.triage_activated:
        session_service.mark_triage_activated(session)
    if triage.human_handoff:
        session_service.mark_handoff(session)

    logger.info(
        "Stream started: session_id=%s, risk_score=%d, triage=%s",
        session.id, risk_score, triage.triage_activated,
    )

    async def event_generator():
        """Generate SSE events, streaming tokens from the LLM in real time."""
        metadata = {
            "type": "metadata",
            "session_id": session.id,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "triage_activated": triage.triage_activated,
            "human_handoff": triage.human_handoff,
        }
        yield f"data: {json.dumps(metadata)}\n\n"

        if triage.crisis_resources:
            crisis_data = {
                "type": "crisis",
                "resources": [r.model_dump() for r in triage.crisis_resources],
            }
            yield f"data: {json.dumps(crisis_data)}\n\n"

        if triage.override_response:
            # Triage override: fake-stream the canned response
            words = triage.override_response.split(" ")
            for i, word in enumerate(words):
                token = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                await asyncio.sleep(STREAM_TOKEN_DELAY_SECONDS)
            bot_response = triage.override_response
        else:
            # Stream tokens from the LLM in real time
            bot_response = ""
            async for token in chatbot.stream_response(request.user_message, session):
                if token.startswith("__REPLACE__"):
                    # Validation replaced the response
                    replacement = token[len("__REPLACE__"):]
                    replace_data = {"type": "replace", "content": replacement}
                    yield f"data: {json.dumps(replace_data)}\n\n"
                    bot_response = replacement
                else:
                    bot_response += token
                    token_data = {"type": "token", "content": token}
                    yield f"data: {json.dumps(token_data)}\n\n"

        session_service.add_bot_message(session, bot_response)

        done_data = {
            "type": "done",
            "session_message_count": session.message_count,
        }
        yield f"data: {json.dumps(done_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{session_id}/history",
    response_model=SessionHistoryResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get session history",
    description="Retrieve the full conversation history for a session.",
)
def get_history(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> SessionHistoryResponse:
    """Return the full conversation history for a session.

    Args:
        session_id: Session identifier.
        session_service: Injected session service.

    Returns:
        SessionHistoryResponse with ordered message list.

    Raises:
        HTTPException: If session is not found.
    """
    try:
        session = session_service.get_session(session_id)
    except SessionNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    history = [
        MessageEntry(
            role=msg.role,
            content=msg.content,
            risk_score=msg.risk_score,
            timestamp=msg.timestamp,
        )
        for msg in session.messages
    ]

    return SessionHistoryResponse(
        session_id=session.id,
        history=history,
        message_count=session.message_count,
        cumulative_risk=session.cumulative_risk,
        triage_activated=session.triage_activated,
        created_at=session.created_at,
    )


@router.post(
    "/{session_id}/handoff",
    response_model=HandoffResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Trigger manual handoff",
    description="Manually initiate a professional handoff for a session.",
)
def trigger_handoff(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> HandoffResponse:
    """Manually trigger a professional handoff for a session.

    Builds a professional context summary including conversation
    history, risk assessment, and session metadata.

    Args:
        session_id: Session identifier.
        session_service: Injected session service.

    Returns:
        HandoffResponse with professional context.

    Raises:
        HTTPException: If session is not found.
    """
    try:
        session = session_service.get_session(session_id)
    except SessionNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    session_service.mark_handoff(session)
    session_service.mark_triage_activated(session)

    professional_context = _build_professional_context(session)

    logger.info("Manual handoff triggered: session_id=%s", session.id)

    return HandoffResponse(
        session_id=session.id,
        handoff_status="initiated",
        professional_context=professional_context,
    )


def _build_professional_context(session) -> dict:
    """Build a summary context for the incoming professional.

    Args:
        session: The session being handed off.

    Returns:
        Dictionary with conversation summary and risk information.
    """
    recent_messages = session.messages[-5:] if session.messages else []
    return {
        "session_id": session.id,
        "message_count": session.message_count,
        "duration_minutes": round(session.duration_minutes, 1),
        "current_risk_level": session.current_risk_level.value,
        "cumulative_risk": session.cumulative_risk,
        "high_risk_count": session.high_risk_count,
        "triage_activated": session.triage_activated,
        "recent_messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "risk_score": msg.risk_score,
            }
            for msg in recent_messages
        ],
    }
