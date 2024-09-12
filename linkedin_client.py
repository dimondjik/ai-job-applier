import logging

from browser_client import BrowserClient
from config_manager import ConfigManager
from llm_client import LLMClient
from utils import wait_extra
from log_writer import LogWriter

from custom_types.field import FieldTypeEnum

from custom_exceptions import EasyApplyException

logger = logging.getLogger("LinkedInClient")

NEXT_PAGE_DELAY = (4., 8.)


class LinkedInClient:
    def __init__(self):
        """
        Essentially a bot class for LinkedIn, uses all other classes to apply for jobs
        """

        self.browser_client = BrowserClient()
        self.config = ConfigManager()
        self.llm_client = LLMClient()
        self.custom_logger = LogWriter()

    def __apply_to_job(self, easy_apply_form):
        for form_field in self.browser_client.get_form_fields(easy_apply_form):
            if form_field is None:
                break

            if form_field.type == FieldTypeEnum.LIST:
                res, answer = self.llm_client.answer_with_options(form_field.label, form_field.data)
                if res:
                    BrowserClient.set_dropdown_field(form_field.element, answer)
                else:
                    return False

            elif form_field.type == FieldTypeEnum.RADIO:
                res, answer = self.llm_client.answer_with_options(form_field.label, form_field.data)
                if res:
                    BrowserClient.set_radio_field(form_field.element, answer)
                else:
                    return False

            elif form_field.type == FieldTypeEnum.INPUT:
                res, answer = self.llm_client.answer_freely(form_field.label)
                if res:
                    BrowserClient.set_input_field(form_field.element, answer)

                    # In the text input field the suggestions list can appear, check every time
                    suggestions_element, suggestions_options = self.browser_client.is_suggestions_list_appeared()
                    if suggestions_element is not None:
                        res, answer = self.llm_client.answer_with_options(form_field.label, suggestions_options)
                        if res:
                            self.browser_client.set_suggestions_list(suggestions_element, answer)
                        else:
                            return False

                else:
                    return False

            # TODO: Upload something else, based on filters
            elif form_field.type == FieldTypeEnum.UPLOAD_CV:
                BrowserClient.upload_file(form_field.element,
                                          "C:/Users/User/Desktop/Dmitrii-Gorbachev-Gameplay-Developer.pdf")

            elif form_field.type == FieldTypeEnum.UPLOAD_COVER:
                logger.warning("Cover letter upload not implemented yet ^_^")
                return False

            else:
                logger.error(f"LinkedIn client got field type it doesn't recognize ({form_field.type})")
                return False

        return True

    def start(self) -> None:
        self.browser_client.initialize()

        search_url_list = self.browser_client.make_search_urls()

        if search_url_list:
            for search_url in search_url_list:
                job_generator = self.browser_client.get_jobs_from_search_url(search_url)

                while True:
                    try:
                        job = job_generator.__next__()
                        if job is None:
                            break
                        if job.applied:
                            logger.info("Skipping, already applied")
                            continue

                        self.browser_client.get_job_description_and_hiring_team(job)

                        form_element = self.browser_client.get_easy_apply_form()

                        self.__apply_to_job(form_element)

                        self.browser_client.finalize_easy_apply()

                        self.custom_logger.log_success(job)

                        wait_extra(extra_range_sec=NEXT_PAGE_DELAY)

                    except EasyApplyException as ex:
                        self.custom_logger.log_error(ex.data)
                        # If bail out fails - everything fails :)
                        self.browser_client.bail_out()
                        continue

        else:
            logger.error("Can't construct a single search url!")
            return None
