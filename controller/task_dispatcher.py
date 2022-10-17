from threading import Thread

import paho.mqtt.client as mqtt
import json

controller_ip = "localhost"

# mqtt topics
offloader_controller_task_submit_topic = "offl-ctrl-task-submit"  # sub
offloader_controller_task_response_topic = "offl-ctrl-task-response"  # pub

offloader_controller_feedback_request_topic = "offl-ctrl-feedback-request"  # pub
offloader_controller_feedback_response_topic = "offl-ctrl-feedback-response"  # sub

controller_executor_task_execute_topic = "ctrl-exec-task-execute"  # pub
controller_executor_task_response_topic = "ctrl-exec-task-response"  # sub

controller_executor_state_topic = "ctrl-exec-state"  # sub


# TODO update
def request_feedback(self, task_id, feedback):
    pass


def on_connect(client, userdata, flags, rc):
    print("[task_dispatcher] connected to mqtt with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(offloader_controller_task_submit_topic)
    client.subscribe(offloader_controller_feedback_response_topic)
    client.subscribe(controller_executor_task_response_topic)
    client.subscribe(controller_executor_state_topic)


def on_message(client, userdata, mqtt_message):
    # mqtt_message is of type MQTTMessage. Has fields topic, payload,..
    topic = mqtt_message.topic
    payload = mqtt_message.payload

    # print(mqtt_message)
    # print(topic)
    print(payload)

    if topic == offloader_controller_task_submit_topic:
        # try:
        #     message_json = json.loads(payload)
        #     print(message_json)
        #     offloaded_task_id = message_json["offloaded_task_id"]
        #     response = message_json["response"]
        #
        #     print(f"[offl -> ctrl] new task received. ")
        #
        #     print(f'{offloaded_task_id}, {response}')
        # except Exception as e:
        #     print(e)
        pass
    elif topic == offloader_controller_feedback_response_topic:
        pass
    elif topic == controller_executor_task_response_topic:
        pass
    elif topic == controller_executor_state_topic:
        pass


def on_disconnect(client, userdata, rc=0):
    print("DisConnected result code " + str(rc))
    client.loop_stop()


def connect():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect("localhost", 1883, 60)
    client.loop_forever()


def on_publish(client,userdata,result):
    print("data published \n")


class TaskDispatcher:
    def __init__(self):
        # The callback for when the client receives a CONNACK response from the server.
        clientloop_thread = Thread(target=connect)
        clientloop_thread.start()

    def submit_task(self, device_id, task_id, input_data, deadline):
        print("received with thanks")

        # request rl scheduler to schedule this task
