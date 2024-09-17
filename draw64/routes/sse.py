import asyncio
import logging

from typing import cast

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from draw64.event import ImageEventMessage
from draw64.pubsub import announcer
from draw64.state import stop_event

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_announces():
    message_id = 1
    message_queue = announcer.subscribe()
    try:
        while not stop_event.is_set():
            message = cast(ImageEventMessage, await message_queue.get())
            yield ServerSentEvent(
                data=message.model_dump_json(),
                event=message.event.event_type,
                id=str(message_id),
            )
            message_id += 1
    except asyncio.CancelledError:
        logger.info("Client terminated SSE connection.")
    finally:
        announcer.unsubscribe(message_queue)


@router.get("/sse/announce", include_in_schema=False)
async def server_sent_event_annouce():
    return EventSourceResponse(get_announces(), send_timeout=5)
