import json
import threading
import time

import log
import stats

# MQTT executor state topic.
MQTTTopicExecutorStateTopic = "exec-ctrl-state"

def start_state_publisher(controller_addr):
    t = threading.Thread(name='state-publisher',
                         target=__publisher_entry,
                         args=(controller_addr,))
    t.start()

    return t

def __publisher_entry(controller_addr):
    '''Entry point for publisher thread.

    Sends current executor state every five seconds.
    '''

    import paho.mqtt.publish as publish

    log.i('started')

    while True:
        log.d('collecting state')
        stats_message = json.dumps(stats.fetch())
        try:
            log.d('sending current state')
            publish.single(
                MQTTTopicExecutorStateTopic,
                payload=stats_message,
                hostname=controller_addr)
        except ConnectionRefusedError:
            log.e('could not publish state to {}'.format(controller_addr))

        time.sleep(5)
