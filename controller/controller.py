from server import ControllerServer
from task_dispatcher import TaskDispatcher

# start the task dispatcher
task_dispatcher = TaskDispatcher()

# start the http server
controller_server = ControllerServer(task_dispatcher)
controller_server.start_server()

