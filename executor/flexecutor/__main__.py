import argparse
import time

import executor
import log
import service

def main(args):
    log.set_level(args.log_level)
    state_http_server_thread = service.start_state_server()
    executor_server_thread = executor.start_executor(
        args.controller, args.id)

    # Idle around.
    while True:
        time.sleep(3)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='fReeLoaders executor.')
    ap.add_argument('-l', '--log-level', help='Set the logging level.',
                    metavar='LEVEL', choices=['e', 'w', 'i', 'd'])
    ap.add_argument('controller', help='Address of the controller.',
                    metavar='ADDR')
    ap.add_argument('id', help='ID the executor should use.',
                    metavar='NUM', type=int)

    args = ap.parse_args()

    main(args)
