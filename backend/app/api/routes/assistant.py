from fastapi import APIRouter, HTTPException

from app.schemas.assistant import AssistantRequest
from app.services.assistant_service import AssistantService


router = APIRouter(
    prefix="/api/assistant",
    tags=["assistant"],
)


@router.post("")
def process_assistant_request(
    request: AssistantRequest,
):
    assistant_service = AssistantService()

    try:
        return assistant_service.process(
            request.message
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )