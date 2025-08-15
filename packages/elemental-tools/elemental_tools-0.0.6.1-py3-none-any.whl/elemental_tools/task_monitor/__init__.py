import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import sleep
from tqdm import tqdm
from icecream import ic

from elemental_tools.logger import Logger
from elemental_tools.api import TaskController, TaskModel
from elemental_tools.api.controllers.exceptions import TaskTimeoutException
from elemental_tools.config import log_path, thread_limit
from elemental_tools.exceptions import ParameterMissing, ThreadLimitExceeded, ThreadTimeout
from elemental_tools.pydantic.config import default_arguments
from elemental_tools.scripts.install import run as install_scripts

module_name = 'task-monitor'

logger = Logger(app_name=module_name, owner='manager', destination=log_path).log

timeout = 100000

current_threads = []
current_thread_count = 0


def execute_function_with_thread_pool(func, args: dict = None, timeout: int = None):
    global current_thread_count

    if current_thread_count >= thread_limit:
        raise ThreadLimitExceeded("Thread limit exceeded.")

    if args is None:
        return func()

    with ThreadPoolExecutor(max_workers=thread_limit) as executor:
        future = executor.submit(func, **args)

        try:
            result = future.result(timeout=timeout)
        except TimeoutError:
            raise ThreadTimeout("Thread execution exceeded the timeout.")
        except Exception as e:
            raise e

    return result


def execute_function(func, args: dict = None):

    # process no arguments scripts
    if args is None:
        result = func()
        return result
    # process keyword arguments and not keyword arguments
    try:
        result = func(**args)
    except TypeError:
        try:
            result = func(*args.values())
        except TypeError as e:
            raise ParameterMissing(str(e))
    return result


def execute_multi_processing_function(database, task_id, func, args: dict = None):
    pll_process = multiprocessing.Process(target=execute_function, args=(func, args))
    pll_process.run()
    database.set_state(task_id)


class Monitor:
    database = TaskController()
    install_scripts()

    _lc = 0
    start_time = datetime.now()
    uptime = None

    def __init__(self, *script_pydantic_models, debug: bool = False):
        self.script_pydantic_models = {}
        self.debug = debug

        for model in script_pydantic_models:
            if model is not None:
                self.script_pydantic_models.update(model)

        self.uptime = datetime.now() - self.start_time

    def check_for_loop_tasks(self):
        # query all task schedule
        self._lc += 1
        self.uptime = datetime.now() - self.start_time

        if self.debug:

            logger('info', f"Initializing Task Monitor Run Number: {str(self._lc)}", uptime=f"Uptime: {str(abs(self.uptime))}")

        current_loop_tasks = self.database.query_not_processed_tasks()
        results = {}
        errors = []

        if current_loop_tasks:

            for task in tqdm(current_loop_tasks, desc="Running Tasks..."):
                _task_model = TaskModel(**task)

                logger('info', f"Initializing Task: {str(task)}", owner=str(task['task_name']))
                self.database.set_last_execution(task['_id'])
                self.database.set_state(task['_id'], 'Running')
                current_task_name = task['task_name']
                try:
                    current_task_parameters = task['parameters']
                except KeyError:
                    current_task_parameters = {}
                for default_argument in default_arguments:
                    try:
                        current_task_parameters[default_argument] = task[default_argument]
                    except KeyError:
                        raise ParameterMissing(default_argument)
                current_task_function = self.script_pydantic_models[current_task_name]['function']
                try:
                    # results[current_task_name] = execute_function(current_task_function, current_task_parameters)
                    execute_multi_processing_function(database=self.database, task_id=task['_id'], func=current_task_function, args=current_task_parameters)

                except Exception as e:
                    results[current_task_name] = str(e)
                    errors.append(task['_id'])
                    self.database.set_state(task['_id'])
                    logger('error', f"Failure executing {current_task_name}")
                try:
                    if task['loops'] is not None and task['loops'] != 0:
                        self.database.set_loop_count(task['_id'], int(task['loops'])-1)
                except:
                    pass

            logger('success', f"LoopTasks were run successfully")
            logger('info', f"Loop tasks results: {str(results)}")
        elif self.debug:
            logger('nothing', f"No loop tasks found. Skipping execution.")

        return results, errors

    def run(self, timeout: int = None):
        """

        :param timeout: Represents the number of seconds to wait between loops
        :return:
        """

        _loop_tasks_results = None
        _loop_tasks_errors = None
        while True:
            try:
                while True:

                    _loop_tasks_results, _loop_tasks_errors = self.check_for_loop_tasks()

                    if timeout is not None:
                        sleep(timeout)

                    for _error in _loop_tasks_errors:
                        TaskTimeoutException(_error)

            except Exception as e:

                if _loop_tasks_results is not None or _loop_tasks_results is not None:
                    logger("alert", f"""Task are not so well. Here's your Monitor Report on: \n\n\tResults: {_loop_tasks_results}\n\n\tErrors: {_loop_tasks_errors}""")
                    try:
                        logger('critical', f"Task loop breaks during: {list(_loop_tasks_results)} because of exception: {str(e)}'")

                    except KeyError:
                        logger("critical", f"Task loop breaks during initialization. It must be serious.")

                sleep(15)
