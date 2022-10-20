import functools
import os

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
    gpu_stats = _gpu_stats()

    state = {
        'cpu-load': psutil.getloadavg()[0],
        'free-ram': mem.available,
        'total-ram': mem.total,
        'free-vram': gpu_stats['free-vram'],
        'total-vram': gpu_stats['total-vram'],
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


def _gpu_stats():
    '''Fetch GPU usage information, if available.

    Has special handling for NVIDIA Jetson SBCs.
    '''

    stats = {
        'usage': 0,
        'free-vram': 0,
        'total-vram': 0,
    }

    # Look at the kernel build to tell if this is a Jetson SBC.
    if os.uname().release.endswith('-tegra'):
        import jtop
        with jtop.jtop() as jetson_ctx:
            if jetson_ctx.ok():
                stats['usage'] = jetson_ctx.stats['GPU']
                # Note: SoC shares RAM between CPU and GPU.
                stats['free-vram'] = jetson_ctx.stats['RAM']
                stats['total-vram'] = psutil.virtual_memory().total

    return stats
