"""
AI Generation endpoints: create, list, retrieve, delete, stream.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.models import User, GenerationType
from app.schemas.schemas import (
    GenerationRequest, GenerationResponse, GenerationListResponse, MessageResponse
)
from app.services.generation_service import generation_service
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/generate", tags=["AI Generation"])


@router.post(
    "",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI generation",
    description=(
        "Generate text, code, analysis, or summaries using AI. "
        "Token usage is tracked against your monthly quota. "
        "Optionally attach to a conversation thread for context."
    ),
)
async def create_generation(
    data: GenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    gen = await generation_service.create(db, current_user, data)
    await db.commit()
    await db.refresh(gen)
    return gen


@router.post(
    "/stream",
    summary="Stream AI generation via Server-Sent Events",
    description="Returns a streaming response with tokens as they're generated.",
)
async def stream_generation(
    data: GenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream tokens via Server-Sent Events (SSE)."""
    ai = get_ai_service()

    async def event_generator():
        try:
            async for token in ai.stream_generate(
                prompt=data.prompt,
                generation_type=data.type,
                system_prompt=data.system_prompt,
                temperature=data.temperature or 0.7,
                max_tokens=data.max_tokens or 1024,
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

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
    "",
    response_model=GenerationListResponse,
    summary="List your generations",
)
async def list_generations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[GenerationType] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * size
    items, total = await generation_service.list_for_user(
        db, current_user.id, skip=skip, limit=size, gen_type=type
    )
    import math
    return GenerationListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
    summary="Get a specific generation",
)
async def get_generation(
    generation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await generation_service.get_by_id(db, generation_id, current_user.id)


@router.delete(
    "/{generation_id}",
    response_model=MessageResponse,
    summary="Delete a generation",
)
async def delete_generation(
    generation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await generation_service.delete(db, generation_id, current_user.id)
    await db.commit()
    return MessageResponse(message="Generation deleted successfully")
