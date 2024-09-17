from asyncio import Event

from draw64.image_collection import ImageCollection
from draw64.pubsub import PubSub, SimplePubSub


collection = ImageCollection()
pubsub = PubSub()
announcer = SimplePubSub()
stop_event = Event()
