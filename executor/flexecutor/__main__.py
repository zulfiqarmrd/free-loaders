import argparse
import time

import config
import executor
import log
import multiprocessing
import os
import service
import signal
import stats
import sys
import threading

__Children = {
    'executor': None
}

def main(args):
    __configure_signals()

    # Set the logging level as an environment variable.
    if config.LoggingEnvVar not in os.environ:
        os.environ[config.LoggingEnvVar] = args.log_level

    # Perform boring configuration.
    config.configure_process()

    threading.current_thread().name = 'top'

    gpu_monitor_thread = stats.start_gpu_monitor_thread()
    state_http_server_thread = service.start_state_server()
    __Children['executor'] = __start_executor(
        args.controller, args.id, args.log_level)

    # Idle around.
    while True:
        # Wait for a process to end.
        sentinels = [__Children['executor'].sentinel]
        mp_event = multiprocessing.connection.wait(sentinels)

        if not __Children['executor'].is_alive():
            log.w('executor died')
            __Children['executor'] = __start_executor(
                args.controller, args.id, args.log_level)

def __start_executor(controller_addr, executor_id, log_level):
    log.i('starting executor')
    proc = executor.start_executor(controller_addr, executor_id, log_level)
    log.i('started executor (PID {})'.format(proc.pid))

    return proc

def __configure_signals():
    signums = [signal.SIGINT, signal.SIGTERM]
    for signum in signums:
        signal.signal(signum, __signal_handler)

def __signal_handler(signal_no, stack_frame):
    log.i('terminating flexecutor')
    for child in __Children.keys():
        proc = __Children[child]
        if proc.is_alive():
            log.d('terminating child {} (PID {})'.format(child, proc.pid))
            proc.terminate()

    sys.exit(0)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='fReeLoaders executor.')
    ap.add_argument('-l', '--log-level', help='Set the logging level.',
                    metavar='LEVEL', choices=['e', 'w', 'i', 'd'],
                    dest='log_level', default='e')
    ap.add_argument('controller', help='Address of the controller.',
                    metavar='ADDR')
    ap.add_argument('id', help='ID the executor should use.',
                    metavar='NUM', type=int)

    args = ap.parse_args()

    main(args)
