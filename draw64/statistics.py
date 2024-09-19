import asyncio

from collections import defaultdict
from typing import cast

from pydantic import BaseModel

from draw64.event import EventMessage
from draw64.event_factory import make_user_count_updated_message
from draw64.pubsub import announcer, pubsub, SubscribedQueue


class Statistics(BaseModel):
    images_created: int = 0
    images_deleted: int = 0
    user_count: int = 0
    image_updates: defaultdict[str, int] = defaultdict(int)


statistics = Statistics()


async def update_statistics_from_announcer():
    announcer_queue = announcer.subscribe()

    while True:
        message = await announcer_queue.get()
        event = cast(EventMessage, message).event
        if event.event_type == "image_created":
            statistics.images_created += 1
        elif event.event_type == "image_deleted":
            statistics.images_deleted += 1
        elif event.event_type == "user_connected":
            statistics.user_count += 1
        elif event.event_type == "user_disconnected":
            statistics.user_count -= 1

        if event.event_type in ("user_connected", "user_disconnected"):
            announcer.broadcast(make_user_count_updated_message(statistics.user_count))


async def update_statistics_from_pubsub():
    announcer_queue = announcer.subscribe()
    image_queues: dict[str, SubscribedQueue] = {}

    while True:
        tasks = [
            asyncio.create_task(queue.get(), name=f"image_id_{image_id}")
            for image_id, queue in image_queues.items()
        ]
        tasks.append(asyncio.create_task(announcer_queue.get(), name="announcer_queue"))

        done_tasks, pending_tasks = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        for pending in pending_tasks:
            pending.cancel()

        for done in done_tasks:
            result = done.result()
            event = cast(EventMessage, result).event
            # image_created and image_deleted are sent via the annoucer
            if event.event_type == "image_created":
                image_queues[event.image_id] = pubsub.subscribe(event.image_id)
            elif event.event_type == "image_deleted":
                image_queues[event.image_id].unsubscribe()
            # image_updated is sent via the pubsub
            elif event.event_type == "image_updated":
                statistics.image_updates[event.image_id] += 1
