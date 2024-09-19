import asyncio
import logging

from typing import cast

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from draw64.event import EventMessage
from draw64.pubsub import announcer

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_announces():
    message_id = 1
    message_queue = announcer.subscribe()
    try:
        while True:
            message = cast(EventMessage, await message_queue.get())
            yield ServerSentEvent(
                data=message.model_dump_json(),
                event=message.event.event_type,
                id=str(message_id),
            )
            message_id += 1
    except asyncio.CancelledError as e:
        logger.info("Client terminated SSE connection.")
        raise e
    finally:
        announcer.unsubscribe(message_queue)


@router.get("/sse/announce", include_in_schema=False)
async def server_sent_event_annouce():
    return EventSourceResponse(
        get_announces(),
        send_timeout=5,
        ping=5,
        headers={"Cache-Control": "no-cache, no-store"},
    )
