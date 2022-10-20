from threading import Thread
import paho.mqtt.client as mqtt
import json
import sys

if len(sys.argv) != 3:
    print("usage: python executer.py <executer_id> <controller_ip>")
    sys.exit(1)

executer_id = int(sys.argv[1])
controller_ip = sys.argv[2]

# mqtt topics
controller_executer_task_execute_topic = "ctrl-exec-task-execute"  # sub
executer_controller_task_response_topic = "exec-ctrl-task-response"  # pub

# TODO update this
def execute_task(offload_id, task_id, input_data, on_execution_finished):
    print(f"[executer] executing task with offload_id {offload_id}")
    on_execution_finished(offload_id, "this is the response")


def on_connect(client, userdata, flags, rc):
    print("[executer] connected to mqtt with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(controller_executer_task_execute_topic)

# TODO update this
def get_system_state():
    return ""

def on_task_execution_finished(offload_id, task_response):
    state = get_system_state()
    executer_response = {
        "offload_id": offload_id,
        "response": task_response,
        "state": state
    }
    mqtt_client.publish(executer_controller_task_response_topic, json.dumps(executer_response).encode('utf-8'))
    print(f"[executer] response for offload_id {offload_id} sent to controller")


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
        if topic == controller_executer_task_execute_topic:
            if int(message_json["executer_id"]) == executer_id:
                offload_id = message_json["offload_id"]
                task_id = message_json["task_id"]
                input_data = message_json["input_data"]

                print(f"[executer] task received for execution with offload_id {offload_id}")
                execute_task(offload_id, task_id, input_data, on_task_execution_finished)


def on_disconnect(client, userdata, rc=0):
    print("DisConnected result code " + str(rc))
    client.loop_stop()


def connect(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect("localhost", 1883, 60)
    client.loop_forever()


def on_publish(client,userdata,result):
    print("data published \n")

mqtt_client = mqtt.Client()

# The callback for when the client receives a CONNACK response from the server.
clientloop_thread = Thread(target=connect, args=(mqtt_client,))
clientloop_thread.start()