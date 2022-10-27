import functools
import multiprocessing
import os
import threading
import time

import psutil

import log

def start_gpu_monitor_thread():
    '''Starts a GPU-monitoring thread.
    '''

    t = threading.Thread(name='gpu-monitor',
                         target=__gpu_load_entry)
    t.start()

    return t

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
        'cpu-count': os.cpu_count(),
        'cpu-load': psutil.getloadavg()[0],
        'free-ram': mem.available,
        'total-ram': mem.total,
        'has-gpu': gpu_stats['has-gpu'],
        'gpu-load': gpu_stats['load'],
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
        'has-gpu': 0,
        'load': 0,
        'free-vram': 0,
        'total-vram': 0,
    }

    # Look at the kernel build to tell if this is a Jetson SBC.
    if os.uname().release.endswith('-tegra'):
        import jtop
        stats['has-gpu'] = 1
        with jtop.jtop() as jetson_ctx:
            if jetson_ctx.ok():
                stats['load'] = _get_gpu_load()
                # Note: SoC shares RAM between CPU and GPU.
                stats['free-vram'] = jetson_ctx.stats['RAM']
                stats['total-vram'] = psutil.virtual_memory().total

    return stats

__GPULoad = 0
__GPULoadCollectInterval = .25
__GPULoadHistory = 60 / __GPULoadCollectInterval
__GPUUsagesCollected = 0.0
__GPULoadLock = multiprocessing.Lock()

def __gpu_load_entry():
    '''Entry point for GPU monitoring thread.
    '''

    global __GPULoad
    global __GPULoadHistory
    global __GPUUsagesCollected
    global __GPULoadLock

    log.i('started')

    if os.uname().release.endswith('-tegra'):
        # Collect load information.
        import jtop
        with jtop.jtop() as jetson_ctx:
            while True:
                if jetson_ctx.ok():
                    current_gpu_usage = jetson_ctx.stats['GPU']
                    if __GPUUsagesCollected < __GPULoadHistory:
                        __GPUUsagesCollected = __GPUUsagesCollected + 1

                    __GPULoadLock.acquire()
                    if __GPUUsagesCollected == 1:
                        __GPULoad = current_gpu_usage
                    else:
                        __GPULoad = (__GPULoad * (__GPUUsagesCollected - 1) / __GPUUsagesCollected) + (current_gpu_usage * (1.0 / __GPULoadHistory))
                    log.d('gpu-load: {}'.format(__GPULoad))
                    __GPULoadLock.release()
                else:
                    log.e('unable to collect GPU load data')
                    time.sleep(3)
            time.sleep(__GPULoadCollectInterval)
    else:
        log.i('GPU monitor exiting because nothing to monitor')
        return

def _get_gpu_load():
    '''Returns the value for GPU load.
    '''

    global __GPULoad
    global __GPULoadHistory
    global __GPUUsagesCollected
    global __GPULoadLock
    __GPULoadLock.acquire()
    l = __GPULoad
    __GPULoadLock.release()

    return l
