import asyncio
import logging

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from draw64.state import announcer, stop_event

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_announces():
    message_queue = announcer.subscribe()
    try:
        while not stop_event.is_set():
            message = await message_queue.get()
            yield message.model_dump_json()
    except asyncio.CancelledError:
        logger.info("Client terminated SSE connection.")
    finally:
        announcer.unsubscribe(message_queue)


@router.get("/sse/announce", include_in_schema=False)
async def server_sent_event_annouce():
    return EventSourceResponse(get_announces(), send_timeout=5)
