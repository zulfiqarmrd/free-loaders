import os
import signal
import threading

import log

LoggingEnvVar = 'FLEXECUTOR_LOGGING'

def configure_process(thread_name=None):
    '''Perform rote per-process configuration.
    '''

    # Return SIGTERM signal handler to the default.
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    # Use the provided logging level setting to set the logging leve.
    # If that parameter was not given by the user, check the environment variable.
    log_level = os.getenv(LoggingEnvVar)

    log.set_level(log_level)

    if thread_name != None:
        threading.current_thread().name = thread_name
