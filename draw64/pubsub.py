from asyncio import Queue
from collections import defaultdict
from typing import Any


class PubSub:
    def __init__(self):
        self._queues: dict[str, set[SubscribedQueue]] = defaultdict(set)

    def subscribe(self, topic: str):
        queue = SubscribedQueue(self, topic)
        self._queues[topic].add(queue)
        return queue

    def unsubscribe(self, topic: str, queue: "SubscribedQueue"):
        self._queues[topic].remove(queue)

    def broadcast(self, topic: str, message: Any):
        for queue in self._queues[topic]:
            queue.put_nowait(message)


class SubscribedQueue(Queue):
    def __init__(self, pubsub: PubSub, topic: str):
        super().__init__()
        self._pubsub = pubsub
        self._topic = topic

    def unsubscribe(self):
        self._pubsub.unsubscribe(self._topic, self)


class SimplePubSub:
    """A pubsub without topics."""

    def __init__(self):
        self._queues: set[Queue] = set()

    def subscribe(self):
        queue = Queue()
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: Queue):
        self._queues.remove(queue)

    def broadcast(self, message: Any):
        for queue in self._queues:
            queue.put_nowait(message)
