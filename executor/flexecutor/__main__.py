import argparse
import time

import log
import service

def main(args):
    log.set_level(args.log_level)
    state_http_server_thread = service.start_state_server()

    # Idle around.
    while True:
        time.sleep(3)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='fReeLoaders executor.')
    ap.add_argument('-l', '--log-level', metavar='LEVEL', help='Set the logging level.',
                    choices=['e', 'w', 'i', 'd'])

    args = ap.parse_args()

    main(args)
