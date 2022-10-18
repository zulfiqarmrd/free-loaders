class Task:
    def __init__(self, offload_id, task_id, device_id, input_data, deadline):
        self.offload_id = offload_id  # the unique id assigned to this freeloaders task
        self.task_id = task_id  # the id of the task to execute (from list of pre-defined tasks)
        self.device_id = device_id  # offloader's device_id
        self.input_data = input_data
        self.deadline = deadline
