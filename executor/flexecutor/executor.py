import json
import log
import multiprocessing
import os
import signal
import sys
import threading
import time
from multiprocessing import Process, Pipe

import paho.mqtt.client

import config
import stats
from tasker.loop import run_loop_task
from tasker.mm import run_mm_task
from tasker.cnn_img_classification import run_img_classification_task


# MQTT server port; fixed to 1883.
MQTTServerPort = 1883

# Topic the controller uses to send tasks for execution to executors.
MQTTTopicExecuteTask = 'ctrl-exec-task-execute'
# Topic the executor uses to send responses back to the controller.
MQTTTopicTaskResponse = 'exec-ctrl-task-response'

def start_executor(controller_addr, executor_id, log_level):
    '''Launches the task executor process.

    Accepts the ID to use as its executor ID, which it uses to listen for work.
    '''

    p = Process(name='executor',
                target=__executor_entry,
                args=(controller_addr, executor_id, log_level))
    p.start()

    return p

def __executor_entry(controller_addr, executor_id, log_level):
    '''Executor thread entry function.

    Listens for MQTT messages carrying tasks to run.
    Spins of new threads to perform work.
    '''

    config.configure_process('executor')
    signal.signal(signal.SIGALRM, __signal_handler)

    log.i('started')

    mqtt_client = paho.mqtt.client.Client(userdata={'executor_id': executor_id})
    mqtt_client.on_connect = __mqtt_on_connect
    mqtt_client.on_message = __mqtt_message_received
    mqtt_client.on_disconnect = __mqtt_on_disconnect

    log.i('connecting to {}:{}'.format(controller_addr, MQTTServerPort))

    # Attempt to connect to the MQTT server.
    # This code has grown an issue since breaking it into a subprocess
    # where the client does not want to connect, just forever hanging
    # somewhere in the client code.
    #
    # We use SIGALRM to get out of this hang and kill the process when this happens.
    # The top fLexecutor process will start the subprocess again and it can then try again,
    # when it is more likely to succeed, for some reason.
    while True:
        try:
            signal.alarm(2)
            mqtt_client.connect(controller_addr, MQTTServerPort)
            break
        except ConnectionRefusedError:
            signal.alarm(0)
            log.e('connection refused')
            time.sleep(2)

    signal.alarm(0)

    log.d('entering MQTT client loop')
    mqtt_client.loop_forever()

def __signal_handler(signal_no, stack_frame):
    '''Signal handler for the executor subprocess.

    This is just used to handle the case if the MQTT connect hangs.
    '''

    if signal_no == signal.SIGALRM:
        log.w('MQTT client did not connect in time; exiting...')
        sys.exit(1)
    else:
        log.e('Unhandled signal {} define the executor signal handler.'.format(signal_no))
        sys.exit(1)

def __mqtt_on_connect(client, userdata, flags, rc):
    log.i('Connected to server with result: {}'.format(rc))
    client.subscribe(MQTTTopicExecuteTask)

def __mqtt_on_disconnect(client, userdata, rc=0):
    log.w('Disconnected from server: {}'.format(rc))

def __mqtt_message_received(client, data, msg):
    log.i('received message (on {})'.format(msg.topic))

    if msg.topic == MQTTTopicExecuteTask:
        task_request = json.loads(msg.payload)
        # Check fields.
        for k in ['task_id', 'executer_id', 'input_data', 'offload_id']:
            if k not in task_request:
                log.w('Task request is malformed.')

        log.i('request to execute: {}'.format(task_request['task_id']))
        # Look at the executor ID to see if the task is really for this instance.
        our_id = data['executor_id']
        if task_request['executer_id'] != data['executor_id']:
            log.d('task not for this instance (ours: {} != requested: {})'.format(
                our_id, task_request['executer_id']))
        else:
            __execute_task(client, task_request)

def __execute_task(client, task_request):
    '''Begin executing a task in a new thread.

    Sends a response to the controller after completion.
    '''

    thread = threading.Thread(target=__executor_task_entry,
                              # Hm. Is the MQTT client thread-safe?
                              args=(client, task_request))
    thread.start()

    return thread

def __executor_task_entry(mqtt_client, task_request):
    (p_recv, p_send) = Pipe([False])
    process = Process(target=__process_task_entry, args=(p_send, task_request))
    process.start()
    log.i('started PID {} for task ID {}, offload ID {}'.format(
        process.pid,
        task_request['task_id'],
        task_request['offload_id']))

    p_send.close()

    try:
        result = p_recv.recv()  # block and waits for data from the process
        process.join()  # wait for process to finish up
        mqtt_client.publish(MQTTTopicTaskResponse,
                            result.encode('utf-8'))
    except (EOFError, OSError):
        log.e(f'process failed with exit code = {process.exitcode}')
        # Collect current state and send it, along with the result.
        current_state = stats.fetch()
        response = {
            'executor_id': task_request['executer_id'],
            'task_id': task_request['task_id'],
            'offload_id': task_request['offload_id'],
            'state': current_state,
            'status': process.exitcode  # inform the controller that we failed
        }
        mqtt_client.publish(MQTTTopicTaskResponse,
                            json.dumps(response).encode('utf-8'))
    finally:
        p_recv.close()
        process.terminate()



def __process_task_entry(pipe, task_request):
    '''Task execution process entry.

    Executes the task and sends the result and state to the controller.
    '''

    config.configure_process()

    log.i('executing task')
    # Execute task here.
    task_id = task_request['task_id']
    res = ""
    if task_id < 50:
        res = run_loop_task(task_request['task_id'], task_request['input_data'])
    elif 50 <= task_id < 100:
        res = run_mm_task(task_request['input_data'])
    elif 100 <= task_id < 150:
        res = run_img_classification_task(task_request['task_id'], task_request['input_data'])
    else:
        print(f'ERROR: task_id {task_id} is undefined')

    log.i('completed executing task')

    # Collect current state and send it, along with the result.
    current_state = stats.fetch()
    response = {
        'executor_id': task_request['executer_id'],
        'task_id': task_request['task_id'],
        'offload_id': task_request['offload_id'],
        'result': res,
        'state': current_state,
        'status': 0
    }
    pipe.send(json.dumps(response))
    pipe.close()
