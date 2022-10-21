from threading import Thread
import paho.mqtt.client as mqtt
import json
import asyncio
from aiohttp import ClientSession, ClientConnectorError

executer_server_port = 8088

# mqtt topics
controller_offloader_task_response_topic = "ctrl-offl-task-response"  # pub

controller_offloader_feedback_request_topic = "ctrl-offl-feedback-request"  # pub
offloader_controller_feedback_response_topic = "offl-ctrl-feedback-response"  # sub

controller_executer_task_execute_topic = "ctrl-exec-task-execute"  # pub
executer_controller_task_response_topic = "exec-ctrl-task-response"  # sub


# TODO update
def request_feedback(self, task_id, feedback):
    pass


async def fetch_json(executer_id: int, url: str, session: ClientSession, **kwargs) -> tuple:
    try:
        print(f'in fetch_json. about to request {url}')
        resp = await session.request(method="GET", url=url, **kwargs)
        print("resp done")
        response_json = await resp.json()
        print(response_json)
    except ClientConnectorError:
        return executer_id, url, 404
    return executer_id, response_json


async def make_requests(url_tuples: list, **kwargs) -> None:
    async with ClientSession() as session:
        tasks = []
        for url_tuple in url_tuples:
            tasks.append(
                fetch_json(executer_id=url_tuple[0], url=url_tuple[1], session=session, **kwargs)
            )
        results = await asyncio.gather(*tasks)

    return results


def on_connect(client, userdata, flags, rc):
    print("[task_dispatcher] connected to mqtt with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(offloader_controller_feedback_response_topic)
    client.subscribe(executer_controller_task_response_topic)


def on_message(client, userdata, mqtt_message):
    # mqtt_message is of type MQTTMessage. Has fields topic, payload,..
    topic = mqtt_message.topic
    payload = mqtt_message.payload

    try:
        message_json = json.loads(payload)
        print(message_json)
    except Exception as e:
        print(e)
    else:
        if topic == offloader_controller_feedback_response_topic:
            pass
        elif topic == executer_controller_task_response_topic:
            # get the response
            offload_id = message_json["offload_id"]
            response = message_json["response"]
            print(f"[task_dispatch] response received for offload_id {offload_id}: {response}")

            del message_json["state"]


            # publish this to the offloader
            client.publish(controller_offloader_task_response_topic, json.dumps(message_json).encode('utf-8'))
            print(f"[task_dispatch] response for offload_id {offload_id} forwarded to offloader")


def on_disconnect(client, userdata, rc=0):
    print("DisConnected result code " + str(rc))
    client.loop_stop()


def connect(mqtt_client):
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_forever()


def on_publish(client,userdata,result):
    print("data published \n")


class TaskDispatcher:
    def __init__(self, rl_scheduler, executers):
        self.rl_scheduler = rl_scheduler
        self.executers = executers
        self.tasks = {}

        self.mqtt_client = mqtt.Client()

        # The callback for when the client receives a CONNACK response from the server.
        clientloop_thread = Thread(target=connect, args=(self.mqtt_client,))
        clientloop_thread.start()

    def send_task_to_executer(self, executer_id, task):
        # publish on mqtt to executer
        # assumption: each executer knows its id
        task_request_msg = {
            "executer_id": executer_id,
            "offload_id": task.offload_id,
            "task_id": task.task_id,
            "input_data": task.input_data
        }
        self.mqtt_client.publish(controller_executer_task_execute_topic, json.dumps(task_request_msg).encode('utf-8'))
        print(f"task sent for execution to executer {self.executers[executer_id].executer_ip}")

    def get_executer_state(self):
        # create a list of all executer ips with a specific http endpoint
        executer_items = list(self.executers.items())
        url_tuples = list(map(lambda item: (item[0], f'http://{item[1].executer_ip}:{executer_server_port}/state'), executer_items))

        print(url_tuples)
        return asyncio.run(make_requests(url_tuples=url_tuples))

    def submit_task(self, task):
        print(f"[task_dispatcher] received task: {task.task_id}")

        # query all executers for their state
        before_state = self.get_executer_state()

        # request rl scheduler to schedule this task
        executer_id = self.rl_scheduler.schedule(before_state, task)

        print(f"[task_dispatcher] task needs to be sent to executer {executer_id}")
        self.send_task_to_executer(executer_id, task)

        # save the task for future reference
        self.tasks[task.offload_id] = task
