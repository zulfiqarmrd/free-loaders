from threading import Thread

import paho.mqtt.client as mqtt
import json

controller_ip = "localhost"
controller_task_submit_topic = "task-submit"
controller_task_response_topic = "task-response"


class Offloader:
    def __init__(self, id):
        self.id = id
        # The callback for when the client receives a CONNACK response from the server.
        clientloop_thread = Thread(target=connect)
        clientloop_thread.start()

    # TODO update
    def offload(self, task_id, input_data, deadline=0):
        pass

    # TODO update
    def send_feedback(self, task_id, feedback):
        pass

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(controller_task_response_topic)


        # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, mqtt_message):
        # mqtt_message is of type MQTTMessage. Has fields topic, payload,..
        topic = mqtt_message.topic
        payload = mqtt_message.payload

        # print(mqtt_message)
        # print(topic)
        print(payload)

        if topic == controller_task_response_topic:
            print("topic match!")
            try:
                message_json = json.loads(payload)
                print(message_json)
                offloaded_task_id = message_json["offloaded_task_id"]
                response = message_json["response"]

                print(f'{offloaded_task_id}, {response}')
            except Exception as e:
                print(e)


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




# TODO: add loop code to submit tasks periodically