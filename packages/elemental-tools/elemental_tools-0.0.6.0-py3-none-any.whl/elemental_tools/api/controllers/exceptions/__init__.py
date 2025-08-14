from elemental_tools.api.controllers import TaskController


class TaskTimeoutException(Exception):

    def __init__(self, _id):
        print(f'Task Timeout Exceeded, Blocking Next Execution for Task ID: {_id}')
        TaskController().set_status(_id, False)
