import http.server

import json
import log
import stats
import threading

HTTPServerPort = 8088

class ExecutorHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_addr, server):
        super().__init__(request, client_addr, server)

    def do_GET(self):
        log.i('{} GET {}'.format(self.client_address[0], self.path))

        if self.path == '/state':
            self.get_state()
        else:
            self.send_response(404)

    def log_message(self, format, *args):
        pass

    def get_state(self):
        state = stats.fetch()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(state).encode('utf-8'))

def start_state_server():
    log.i('Launching executor HTTP server.')
    t = threading.Thread(name='state-http-server',
                         target=__state_server_entry)
    t.start()

    return t

def __state_server_entry():
    listen_addr = ('', HTTPServerPort)
    log.i('HTTP server starting on {}'.format(listen_addr))
    server = http.server.HTTPServer(listen_addr, ExecutorHTTPRequestHandler)
    server.serve_forever()
