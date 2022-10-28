from server import ControllerServer
from task_dispatcher import TaskDispatcher
from rl_scheduler import RLScheduler
from classes.executer import Executer

# TODO remove and add to executers.json
executers = {
    0: Executer(0, "172.27.153.31"),  # nano

    1: Executer(1, "172.27.150.233"),  # rpi3
    2: Executer(2, "172.27.134.111"),  # rpi3

    3: Executer(3, "172.27.138.171"),  # rpi4
    4: Executer(4, "172.27.139.169"),  # rpi4
    5: Executer(5, "172.27.129.215"),  # rpi4
    6: Executer(6, "172.27.184.237"),  # rpi4
    7: Executer(7, "172.27.151.135"),  # rpi4

    8: Executer(8, "172.27.130.255"),  # tx2
    9: Executer(9, "172.27.133.131"),  # desktop
}

# initialize the RLScheduler
rl_scheduler = RLScheduler(executers)

# start the task dispatcher
task_dispatcher = TaskDispatcher(rl_scheduler, executers)

# start the http server to receive tasks from offloaders
controller_server = ControllerServer(task_dispatcher)
controller_server.start_server()
