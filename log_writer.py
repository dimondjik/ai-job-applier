import os
from datetime import datetime
from custom_types.job import Job
from custom_exceptions import EasyApplyExceptionData
from utils import Singleton


class LogWriter(metaclass=Singleton):
    def __init__(self):
        """
        Class for writing job application result log in logs folder
        """

        current_time_postfix = datetime.now().strftime("-%Y_%m_%d-%H_%M_%S")
        self.success_path = os.path.join(".",
                                         "logs",
                                         f"successful{current_time_postfix}.txt")
        self.failed_path = os.path.join(".",
                                        "logs",
                                        f"failed{current_time_postfix}.txt")

        open(self.success_path, "w").close()
        open(self.failed_path, "w").close()

    def log_success(self, job_data: Job) -> None:
        """
        Write successful job application to log

        :param job_data: Job object
        """
        with open(self.success_path, "a") as f:
            f.writelines("{} ({})\n"
                         "{}\n"
                         "Link: {}\n"
                         "--------------------\n".format(job_data.title, job_data.company,
                                                         job_data.location,
                                                         job_data.link))

    def log_error(self, ex_data: EasyApplyExceptionData) -> None:
        """
        Write failed job application to log

        :param ex_data: Custom exception object
        """
        with open(self.failed_path, "a") as f:
            f.writelines("{}\n"
                         "Link: {}\n"
                         "Reason: {}\n"
                         "--------------------\n".format(ex_data.job_title,
                                                         ex_data.job_link,
                                                         ex_data.reason))
