from threading import Thread
import paho.mqtt.client as mqtt
import json
import asyncio
from aiohttp import ClientSession, ClientConnectorError
import time

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
    resp = await session.request(method="GET", url=url, **kwargs)
    response_json = await resp.json()
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


class TaskDispatcher:
    def __init__(self, rl_scheduler, executers):
        self.rl_scheduler = rl_scheduler
        self.executers = executers
        self.mqtt_client = mqtt.Client()
        self.execution_times = {}  # offload_id -> start_time
        self.deadlines = {}  # offload_id -> deadline
        self.deadlines_met = 0
        self.finished_tasks = 0

        # The callback for when the client receives a CONNACK response from the server.
        clientloop_thread = Thread(target=self.connect, args=(self.mqtt_client,))
        clientloop_thread.start()

    def on_connect(self, client, userdata, flags, rc):
        print("[td] connected to mqtt with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(offloader_controller_feedback_response_topic)
        client.subscribe(executer_controller_task_response_topic)

    def on_message(self, client, userdata, mqtt_message):
        # mqtt_message is of type MQTTMessage. Has fields topic, payload,..
        topic = mqtt_message.topic
        payload = mqtt_message.payload

        try:
            message_json = json.loads(payload)
        except Exception as e:
            print(e)
        else:
            if topic == offloader_controller_feedback_response_topic:
                pass
            elif topic == executer_controller_task_response_topic:
                # get the response
                offload_id = message_json["offload_id"]
                state_of_executor = message_json["state"]
                executor_id = message_json["executor_id"]
                task_id = message_json["task_id"]

                if offload_id not in self.execution_times.keys():
                    # ignore a response if we're not expecting it
                    print(f"[td] ignored response for task (offload_id={offload_id}, task_id={task_id}) from executer_id={executor_id}")
                    return

                # compute execution time
                exec_time_ms = (time.time() - self.execution_times[offload_id]) * 1000
                deadline = self.deadlines[offload_id]
                deadline_met = exec_time_ms <= deadline
                print(f"[td] finished task (offload_id={offload_id}, task_id={task_id}) on executer_id={executor_id}. time(ms)={exec_time_ms}, deadline={deadline}, deadline_met={deadline_met}")

                self.finished_tasks += 1
                self.deadlines_met += (1 if deadline_met else 0)
                print(f"[td] deadlines_met={self.deadlines_met},finished_tasks={self.finished_tasks},dsr={self.deadlines_met/self.finished_tasks}")

                # give the feedback to the rl scheduler
                self.rl_scheduler.task_finished(offload_id, exec_time_ms, state_of_executor, str(executor_id))

                del message_json["state"] # exclude state from being sent to the offloader
                # publish this to the offloader
                client.publish(controller_offloader_task_response_topic, json.dumps(message_json).encode('utf-8'))

                # remove the offload_id's execution time and deadline from memory
                del self.execution_times[offload_id]
                del self.deadlines[offload_id]

    def on_disconnect(self, client, userdata, rc=0):
        print("DisConnected result code " + str(rc))
        client.loop_stop()

    def connect(self, mqtt_client):
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.on_message
        mqtt_client.on_disconnect = self.on_disconnect

        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_forever()

    def on_publish(self, client,userdata,result):
        print("data published \n")

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

    def get_executer_state(self):
        # create a list of all executer ips with a specific http endpoint
        executer_items = list(self.executers.items())
        url_tuples = list(map(lambda item: (str(item[0]), f'http://{item[1].executer_ip}:{executer_server_port}/state'), executer_items))
        return dict(asyncio.run(make_requests(url_tuples=url_tuples)))

    def submit_task(self, task):
        print(f"[td] new task(offload_id={task.offload_id}, task_id={task.task_id}, deadline={task.deadline})")

        self.execution_times[task.offload_id] = time.time()
        self.deadlines[task.offload_id] = task.deadline

        # query all executers for their state
        state_of_executors = self.get_executer_state()

        #print(f'[td] before_state = {state_of_executors}')

        # test code
        # executer_id = 0
        # request rl scheduler to schedule this task
        executer_id = self.rl_scheduler.schedule(state_of_executors, task)

        print(f"[td] scheduled task(offload_id={task.offload_id}, task_id={task.task_id}) on executer_id={executer_id}")
        self.send_task_to_executer(executer_id, task)
