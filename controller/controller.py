from server import ControllerServer
from task_dispatcher import TaskDispatcher
from rl_scheduler import RLScheduler
from classes.executer import Executer

# TODO read executors from json
executers = {
    0: Executer(0, "localhost"),
    1: Executer(1, "localhost"),
    2: Executer(2, "localhost"),
    3: Executer(3, "localhost"),
    4: Executer(4, "localhost")
}

# initialize the RLScheduler
rl_scheduler = RLScheduler(executers)

# start the task dispatcher
task_dispatcher = TaskDispatcher(rl_scheduler, executers)

# start the http server to receive tasks from offloaders
controller_server = ControllerServer(task_dispatcher)
controller_server.start_server()
