import functools

import psutil

def fetch():
    '''Returns a dictionary of system state information.

    Includes the following stats:
    - 1-min. CPU load
    - free RAM
    - total RAM installed
    - free VRAM
    - total VRAM
    - no. of processes
    - no. of threads
    '''

    # Get consistent views of these once.
    mem = psutil.virtual_memory()
    (proc_count, thread_count) = _process_thread_count()

    state = {
        'cpu-load': psutil.getloadavg()[0],
        'free-ram': mem.available,
        'total-ram': mem.total,
        'free-vram': 0, # TODO
        'total-vram': 0, # TODO
        'process-count': proc_count,
        'thread-count': thread_count,
    }

    return state

def _process_thread_count():
    pids = psutil.pids()
    process_count = len(pids)
    thread_count = functools.reduce(lambda acc, c: acc + c,
                          map(lambda p: p.num_threads(),
                              psutil.process_iter()),
                          0)

    return (process_count, thread_count)
