import time
import random
from textwrap import indent
import logging

logger = logging.getLogger("Delays")


# Base class with pretty print function, supports nested classes who also have PrettyPrintable as a base class
class PrettyPrintable:
    # Pretty print object fields, YAML-like
    def __str__(self):
        pretty = ""
        # For every property in object
        for k, v in self.__dict__.items():
            # If value even contains something
            if v:
                # If value is a list
                if isinstance(v, list):
                    # If all things in the list are strings or integers
                    if all([isinstance(i, str) or isinstance(i, int) for i in v]):
                        # We can absolutely print these values as list
                        # With key as header
                        # And items indented by "  - "
                        pretty += f"{k}:\n"
                        for v_item in v:
                            pretty += f"  - {v_item}\n"
                    # If all thing in the list are classes derived from PrettyPrintable
                    elif all([isinstance(i, PrettyPrintable) for i in v]):
                        # We can get pretty print from the class
                        # With key as header
                        # Resulting string indented by "    " and fist line by "  - "
                        pretty += f"{k}:\n"
                        for v_item in v:
                            # Splitting by '\n', we should have last empty line, so remove it
                            for i, v_item_line in enumerate(str(v_item).split('\n')[:-1]):
                                if i == 0:
                                    pretty += f"  - {v_item_line}\n"
                                else:
                                    pretty += f"    {v_item_line}\n"
                    # TODO: If value type is not supported do something :)
                    else:
                        pass
                # If value is a string or integer
                elif isinstance(v, str) or isinstance(v, int):
                    # We can just simply print in
                    pretty += f"{k}: {v}\n"
                # If value is pretty printable class
                elif isinstance(v, PrettyPrintable):
                    # Hand over pretty print to that class and indent result by "  "
                    pretty += f"{k}:\n"
                    pretty += "{}".format(indent(str(v), "  "))
                # If value is boolean
                elif isinstance(v, bool):
                    # Handle almost the same way as string
                    pretty += "{}: {}\n".format(k, "true" if v else "false")
                # TODO: If value type is not supported do something :)
                else:
                    pass
        # By now we should have all things printed here, return it
        return pretty


def wait_for(condition_func, timeout=4, check_delay_sec=0.1):
    """
    Wait for something with timeout

    :param condition_func: must be callable with boolean result
    :param timeout: return False after that time
    :param check_delay_sec: frequency at which condition_func will be called
    :return: False if timed out, True if condition_func succeeded before timeout
    """

    logger.info(f"Using wait_for to wait for a condition, timeout is {timeout} seconds")

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

    delay = random.uniform(*extra_range_sec)
    logger.info(f"Using wait_extra to wait for {round(delay, 1)} seconds "
                f"(between {extra_range_sec[0]} to {extra_range_sec[1]} seconds)")

    time.sleep(delay)


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
