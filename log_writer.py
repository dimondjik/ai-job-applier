import os
from datetime import datetime
from custom_types.job import Job
from custom_exceptions import CustomExceptionData
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

        open(self.success_path, "w", encoding="UTF-8").close()
        open(self.failed_path, "w", encoding="UTF-8").close()

    def log_success(self, job_data: Job, cv_pdf_path: str) -> None:
        """
        Write successful job application to log

        :param job_data: Job object
        :param cv_pdf_path: Browser-valid path to the cv sent with this application
        """
        with open(self.success_path, "a", encoding="UTF-8") as f:
            f.writelines(("{} ({})\n"
                          "{}\n"
                          "Link: {}\n"
                          "CV: {}\n" + 120 * "-" + "\n").format(job_data.title, job_data.company,
                                                                job_data.location,
                                                                job_data.link,
                                                                cv_pdf_path))

    def log_error(self, ex_data: CustomExceptionData) -> None:
        """
        Write failed job application to log

        :param ex_data: Custom exception object
        """
        with open(self.failed_path, "a", encoding="UTF-8") as f:
            f.writelines(f"{ex_data}\n" + 120 * "-" + "\n")
