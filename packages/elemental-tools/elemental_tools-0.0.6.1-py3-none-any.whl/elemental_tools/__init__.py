from threading import Thread
import os
from time import sleep


class API:

    def __init__(self, *script_pydantic_models, app_name: str, host: str = "127.0.0.1", port: int = 3000, enable_task_monitor: bool = False):

        from elemental_tools.logger import Logger
        from elemental_tools.config import log_path
        from elemental_tools.patterns import Patterns
        from elemental_tools.db import couch as CouchDB
        from elemental_tools.db import mongo as MongoDB

        from elemental_tools.api import Api, run as run_api
        from elemental_tools.pydantic import generate_pydantic_model_from_path
        from elemental_tools.task_monitor import Monitor

        self.logger = Logger(app_name='api', owner='server', destination=log_path).log

        self.Monitor = Monitor
        self.run_api = run_api

        self.logger('start', message='Starting API...', app_name='api')
        self.app_name = app_name
        self.enable_task_monitor = enable_task_monitor

        self.script_pydantic_models = {}
        for spm in script_pydantic_models:
            if spm is not None:
                for key, value in spm.items():
                    self.script_pydantic_models[key] = value

        self.app = Api(script_pydantic_models=self.script_pydantic_models)

        # set the specs for the api server don't try to run on reload mode, it can break with the thread stuff. For debug, you can use a separate script with non-threaded methods.
        self.api_specs = {
            "app": self.app,
            "host": host,
            "port": port
        }

    def run(self):

        self.logger('start', message='Creating API Thread', app_name=self.app_name)

        if os.getenv('INSTALL', False):
            self.logger('installation', message='Running Database Setup. Remember that you can disable this behaviour by setting the env variable INSTALL to FALSE. See documentation for further information.', app_name=self.app_name)
            from .Jarvis.install import InstallAPI, InstallJarvis

            self.InstallAPI, self.InstallJarvis = InstallAPI, InstallJarvis

            self.InstallJarvis().install()
            self.InstallAPI().install()

            self.logger('success',
                   another_owner='installation',
                   message='Done.',
                   app_name=self.app_name
                )

        # create api thread
        t_api = Thread(target=self.run_api, kwargs=self.api_specs)
        self.logger('start', message=f"""Starting API Thread""", app_name=self.app_name)

        # start
        t_api.start()
        sleep(10)

        if self.enable_task_monitor:
            self.logger('start', message='Creating Task Monitor Instance...', app_name=self.app_name)
            # the same for the monitor feel free to add as many threads you can
            task_monitor = self.Monitor(self.script_pydantic_models)
            self.logger('start', message='Starting Task Monitor...', app_name=self.app_name)
            task_monitor.run(timeout=2)

        t_api.join()

