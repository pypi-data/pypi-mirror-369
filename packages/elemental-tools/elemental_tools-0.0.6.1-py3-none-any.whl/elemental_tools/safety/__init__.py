from datetime import datetime
from functools import wraps
from time import sleep

from elemental_tools.design import UnicodeColors
from elemental_tools.logger import Logger


class InternalClock:

    _sec = 1
    _min = 60
    _hour = _min * 60
    _day = 24 * _hour
    _last_request = None
    _stop_waiting = False
    # Map the unit to seconds
    _unit_to_seconds = {
        'second': _sec,
        'minute': _min,
        'hour': _hour,
        'day': _day
    }
    _requests = {}

    class ExceptionStopWaiting(Exception):

        def __init__(self, message):
            super().__init__(message)


    def __init__(self, logger: Logger.log = None):
        self.logger = logger

    def cooldown_generator(self, cooldown: float):
        ratio = 256
        proportional_cooldown_for_each_sleep = cooldown / ratio
        for duration in [proportional_cooldown_for_each_sleep for i in range(ratio)]:
            yield duration

    def stop_waiting(self):
        self._stop_waiting = True
        return self._stop_waiting

    def limit_reached(self, cooldown: float, _sleep=True):

        if self.logger is not None:
            self.logger('alert', f"Rate limit exceeded. For your phone number safety you are blocked {str(cooldown)} seconds.", new_own='internal-clock-limiter')
        else:
            print(f"{UnicodeColors.red}Rate limit exceeded. For your phone number safety you are blocked {str(cooldown)} seconds.{UnicodeColors.reset}")

        if _sleep:
            while not self._stop_waiting:
                cooldown_chunks = self.cooldown_generator(cooldown)
                for i in cooldown_chunks:
                    sleep(i)
                break
            if self._stop_waiting:
                self._stop_waiting = not self._stop_waiting
                raise self.ExceptionStopWaiting('Someone prevent you from waiting. It looks like something is more important for now.')

    def limiter(self, time_signature: str = '1/second', func=None, enable_sleep=True):
        if func is None:
            func = "__single__"

        """
        Args:
            time_signature: "1/minute", "10/minute", "1/hour", etc.

        Returns:
            Keep on going or block the next phase by raising a violent and abrupt exception error that can make you lose all your live trying to fix it.
        """

        # Extract quantity and unit from time_signature
        quantity, unit = time_signature.split('/')

        # Calculate the time fraction in seconds
        time_fraction = self._unit_to_seconds[unit] / int(quantity)

        # Get the current time
        current_time = datetime.now()

        # Check if there are previous requests
        if self._requests.get(func, None) is not None:
            # Get the time difference between the current time and the last request
            time_difference = current_time - self._requests.get(func)

            # Check if the time difference is less than the allowed time fraction
            if time_difference.total_seconds() < time_fraction:
                _cooldown = float(time_fraction).__format__(".2f")
                # Raise an exception if the limit is exceeded
                self.limit_reached(cooldown=float(_cooldown), _sleep=enable_sleep)

        # Add the current time to the list of requests
        self._requests[func] = current_time

    def limiter_decorator(self, time_signature: str, enable_sleep=True):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.limiter(time_signature, func, enable_sleep=enable_sleep)
                return func(*args, **kwargs)
            return wrapper
        return decorator

