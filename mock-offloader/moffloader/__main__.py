import argparse
import json
import random
import time
import numpy as np

import requests

ControllerHTTPPort = 8001

def main(args):
    if args.task_id == None:
        offload_many(args.address,
                    args.device_id,
                    args.task_count,
                    args.rate)
    else:
        offload_one(args.address,
                    args.device_id,
                    args.task_id)

def offload_many(address, device_id, count, rate):
    intertask_delay = 1 / (rate / 60)
    print('Sending tasks every {} sec.'.format(intertask_delay))

    for i in range(0, count):
        # Send the task.
        task_id = random.randint(0, 149) # Random selection.
        offload_one(address, device_id, task_id)
        time.sleep(intertask_delay)

def offload_one(address, device_id, task_id):
    payload = {
        'device_id': device_id,
        'task_id': task_id,
        'input_data': '',
    }

    if task_id < 50:
        # For loop task.
        payload['input_data'] = 0
        pass
    elif task_id < 100:
        # Matrix multiplication task.
        # Generate a matrix and send it as the input data.
        size = round(20 + ((task_id - 50) * 20))

        a = []
        b = []
        for i in range(0, size):
            ax = []
            bx = []
            for j in range (0, size):
                ax.append(random.randint(0, 999))
                bx.append(random.randint(0, 999))
            a.append(ax)
            b.append(bx)

        payload['input_data'] = {
            'a': a,
            'b': b,
        }

    elif task_id < 150:
        # Image classification task.
        # the image classification batch size is dependent on the task_id, we don't send any input data
        payload['input_data'] = {
        }

    # Send the task to the controller.
    url = 'http://{}:{}/submit-task'.format(address, ControllerHTTPPort)
    body_json = json.dumps(payload)
    # print('Sending task data {}'.format(body_json))
    try:
        response = requests.post(url, data=body_json, headers={'Content-Type': 'application/json'})
        print('Server says {}:', end='')
        for line in response.iter_lines():
            print('{}'.format(line))
    except requests.exceptions.ConnectionError:
        print('...cannot connect to server.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Task offloading utility')
    ap.add_argument('-d', '--device-id', help='Set the device ID.',
                    metavar='ID', type=int, default=0, dest='device_id')
    ap.add_argument('-t', '--task-id', help='Send a specific task.',
                    metavar='ID', type=int, dest='task_id')
    ap.add_argument('-n', '--task-count', help='Total number of tasks to send.',
                    metavar='COUNT', type=int, default=1000, dest='task_count')
    ap.add_argument('-r', '--rate', help='Rate to send tasks at (per min.).',
                    metavar='RATE', type=int, default=1000, dest='rate')

    ap.add_argument('address', help='Controller address')

    args = ap.parse_args()
    main(args)
