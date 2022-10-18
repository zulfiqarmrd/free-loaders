from functools import partial
import socketserver
import json
from http.server import BaseHTTPRequestHandler
from classes.task import Task
import cgi

next_offloaded_task_id = 1
PORT = 8001
DEFAULT_DEADLINE = 5000 # 5 seconds


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, task_dispatcher, *args, **kwargs):
        self.task_dispatcher = task_dispatcher
        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        # receive the task parameters
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers['content-length'])
        post_input_data = json.loads(self.rfile.read(length))
        print(post_input_data)

        # do some sanity checks
        fields = post_input_data.keys()
        if "device_id" not in fields or "task_id" not in fields or "input_data" not in fields:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = "ERROR: some of these fields seem to be missing: device_id, task_id, input_data"
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        # if everything proper, assign a new unique task id to it and send it as response
        global next_offloaded_task_id
        self._set_response()
        response = {
            "offloaded_task_id": next_offloaded_task_id
        }

        # send the unique offloaded_task_id back as response
        self.wfile.write(json.dumps(response).encode('utf-8'))

        # generate a unique task id
        next_offloaded_task_id += 1

        # send the task to the task dispatcher
        device_id = post_input_data["device_id"]
        task_id = post_input_data["task_id"]
        input_data = post_input_data["input_data"]
        deadline = post_input_data["deadline"] if "deadline" in fields else DEFAULT_DEADLINE

        self.task_dispatcher.submit_task(Task(device_id, task_id, input_data, deadline))


class ControllerServer:
    def __init__(self, task_dispatcher):
        self.task_dispatcher = task_dispatcher

    def start_server(self):
        # use partial application to pass task_dispatcher object to MyHTTPRequestHandler.
        # ref: https://stackoverflow.com/a/52046062
        handler = partial(MyHTTPRequestHandler, self.task_dispatcher)

        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print("[server] started serving at port", PORT)
            httpd.serve_forever()