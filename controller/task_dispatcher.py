from threading import Thread

import paho.mqtt.client as mqtt
import json

controller_ip = "localhost"

# mqtt topics
controller_offloader_task_response_topic = "ctrl-offl-task-response"  # pub

controller_offloader_feedback_request_topic = "ctrl-offl-feedback-request"  # pub
offloader_controller_feedback_response_topic = "offl-ctrl-feedback-response"  # sub

controller_executer_task_execute_topic = "ctrl-exec-task-execute"  # pub
executer_controller_task_response_topic = "exec-ctrl-task-response"  # sub

executer_controller_state_topic = "exec-ctrl-state"  # sub


# TODO update
def request_feedback(self, task_id, feedback):
    pass


def on_connect(client, userdata, flags, rc):
    print("[task_dispatcher] connected to mqtt with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(offloader_controller_feedback_response_topic)
    client.subscribe(executer_controller_task_response_topic)
    client.subscribe(executer_controller_state_topic)


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

            # publish this to the offloader
            client.publish(controller_offloader_task_response_topic, json.dumps(message_json).encode('utf-8'))
            print(f"[task_dispatch] response for offload_id {offload_id} forwarded to offloader")

        elif topic == executer_controller_state_topic:
            pass


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

    def submit_task(self, task):
        print(f"[task_dispatcher] received task: {task.task_id}")

        # request rl scheduler to schedule this task
        executer_id = self.rl_scheduler.schedule(task)

        print(f"[task_dispatcher] task needs to be sent to executer {executer_id}")
        self.send_task_to_executer(executer_id, task)

        # save the task for future reference
        self.tasks[task.offload_id] = task
