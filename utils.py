import time
import random


def wait_for(condition_func, timeout=4, check_delay_sec=0.1):
    """
    Wait for something with timeout

    :param condition_func: must be callable with boolean result
    :param timeout: return False after that time
    :param check_delay_sec: frequency at which condition_func will be called
    :return: False if timed out, True if condition_func succeeded before timeout
    """
    start_time = time.time()
    while time.time() < start_time + timeout:
        if condition_func():
            return True
        else:
            time.sleep(check_delay_sec)
    return False


# Wait for random seconds in range
def wait_extra(extra_range_sec=(2., 4.)):
    """
    Just simple random wait

    :param extra_range_sec: range for randomizing amount of seconds to wait
    """
    time.sleep(random.uniform(*extra_range_sec))


def wait_for_extra(condition_func, timeout=4, check_delay_sec=0.1, extra_range_sec=(2., 4.)):
    """
    Combined wait_for and wait_extra, will wait for condition_func to succeed
    and will wait a little more in extra_range_sec

    :param condition_func: must be callable with boolean result
    :param timeout: return False after that time
    :param check_delay_sec: frequency at which condition_func will be called
    :param extra_range_sec: range for randomizing amount of seconds to wait
    :return: False if timed out, True if condition_func succeeded before timeout
    """
    res = wait_for(condition_func, timeout, check_delay_sec)
    wait_extra(extra_range_sec)
    return res


class Singleton(type):
    """
    Base class for creating singleton class, should be derived as metaclass

    https://stackoverflow.com/q/6760685
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
