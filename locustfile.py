import json

from locust import HttpUser, task, between


post_data = json.dumps(
    {
        "command": {
            "command_type": "draw",
            "values": [[0, 0, 0, 0, 0]],
        },
    }
)


class Draw64User(HttpUser):
    wait_time = between(0.005, 0.05)

    @task
    def hello_world(self):
        self.client.put("/images/default", data=post_data)
