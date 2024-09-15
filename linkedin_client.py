import logging

from browser_client import BrowserClient
from config_manager import ConfigManager
from llm_client import LLMClient
from utils import wait_extra
from log_writer import LogWriter

from custom_types import *

from custom_exceptions import EasyApplyException, EasyApplyExceptionData

logger = logging.getLogger("LinkedInClient")

NEXT_SEARCH_PAGE_DELAY = (30., 40.)
NEXT_SEARCH_DELAY = (50., 60.)
NEXT_JOB_APPLICATION_DELAY = (6., 8.)


class LinkedInClient:
    def __init__(self):
        """
        Essentially a bot class for LinkedIn, uses all other classes to apply for jobs.

        Think of this as a human that uses tools to apply
        """

        self.browser_client = BrowserClient()
        self.config = ConfigManager()
        self.llm_client = LLMClient()
        self.custom_logger = LogWriter()

        # For logging purposes
        self.error_message = ""

        # Uh, I can't think of something better
        self.current_job: Job = Job()

        self.current_page = 0

    def __try_no_llm_answer(self, field_type: FieldTypeEnum,
                            field_label: str,
                            field_options: list[str] | None) -> str:
        """
        Function with simple filters to try and answer simple questions without the llm involved

        :param field_type: Field type
        :param field_label: The question
        :param field_options: Options (optional)
        :return: Answer if any
        """
        answer = ""

        if field_type == FieldTypeEnum.INPUT:
            if field_label == "First name":
                answer = self.config.user_info.personal.name
            elif field_label == "Last name":
                answer = self.config.user_info.personal.surname
            elif field_label == "Mobile phone number":
                answer = self.config.user_info.personal.phone_prefix + self.config.user_info.personal.phone
            elif field_label == "LinkedIn Profile":
                answer = self.config.user_info.personal.linkedin

        elif field_type == FieldTypeEnum.LIST:
            if field_label == "Phone country code\nPhone country code":
                answer = next((a for a in field_options if self.config.user_info.personal.phone_prefix in a), "")
            elif field_label == "Email address\nEmail address":
                answer = next((a for a in field_options if self.config.user_info.personal.email == a), "")

        elif field_type == FieldTypeEnum.CHECKBOX:
            # Auto agree on terms and conditions checkbox with these keywords
            if ("terms" in field_options[0].lower()) and ("conditions" in field_options[0].lower()):
                answer = field_options[0]
            # Auto agree on any privacy policies checkbox with these keywords
            elif ("privacy" in field_options[0].lower()) and ("policy" in field_options[0].lower()):
                answer = field_options[0]

        return answer

    def __is_title_or_company_blacklisted(self) -> bool:
        """
        Blacklist function which is partially implemented :)

        :return: True if blacklisted
        """

        # TODO: Make this match-case?
        if self.config.blacklist.blacklist_mode == BlacklistEnum.WHOLE_WORDS:

            split_title = self.current_job.title.lower().strip().split(" ")
            for a in split_title:
                for b in self.config.blacklist.title_keywords:
                    if a == b:
                        logger.info(f"Job blacklisted by keyword \"{a}\"")
                        return True

            company = self.current_job.company.lower().strip()
            for b in self.config.blacklist.company:
                if company == b:
                    logger.info(f"Job blacklisted by company \"{company}\"")
                    return True

            return False

        elif self.config.blacklist.blacklist_mode == BlacklistEnum.PARTIAL_WORDS:
            logger.warning("Partial words blacklist not implemented yet!")
            return False

        elif self.config.blacklist.blacklist_mode == BlacklistEnum.LLM_FILTER:
            logger.warning("LLM filter blacklist not implemented yet!")
            return False

        else:
            logger.error("Unknown blacklist mode!")
            return False

    def __get_local_resume_path_by_title(self) -> str:
        """
        Processes title and if key phrase found - return path to local resume
        :return: absolute path to local resume
        """
        for trigger in self.config.filters.local_resume_trigger:
            split_key_phrase = trigger.key_phrase.lower().strip().split(" ")
            if all(kw in self.current_job.title.lower() for kw in split_key_phrase):
                logger.info(f"Local resume triggered by key phrase {trigger.key_phrase}")
                return trigger.path

        return ""

    # def debug_apply_to_specific_job(self, url):
    #     self.browser_client.initialize()
    #     self.browser_client.driver.get(url)
    #     form_element = self.browser_client.get_easy_apply_form()
    #     self.__apply_to_job(form_element)

    def __apply_to_job(self, easy_apply_form):
        for form_field in self.browser_client.get_form_fields(easy_apply_form):
            if form_field is None:
                break

            # TODO: I have a feeling this monstrosity can be refactored to something more readable
            match form_field.type:
                case FieldTypeEnum.LIST:
                    answer = self.__try_no_llm_answer(form_field.type, form_field.label, form_field.data)
                    if answer:
                        logger.info("Saved a cent!\n"
                                    f"The question: {form_field.label}\n"
                                    f"Local answer: {answer}")

                    else:
                        res, answer = self.llm_client.answer_with_options(form_field.label, form_field.data)
                        if not res:
                            self.error_message = (f"LLM did not produce answer.\n"
                                                  f"Question was: {form_field.label}")
                            return False

                    BrowserClient.set_dropdown_field(form_field.element, answer)

                case FieldTypeEnum.RADIO:
                    res, answer = self.llm_client.answer_with_options(form_field.label, form_field.data)
                    if not res:
                        self.error_message = (f"LLM did not produce answer.\n"
                                              f"Question was: {form_field.label}")
                        return False

                    BrowserClient.set_radio_field(form_field.element, answer)

                case FieldTypeEnum.INPUT:
                    answer = self.__try_no_llm_answer(form_field.type, form_field.label, form_field.data)
                    if answer:
                        logger.info("Saved a cent!\n"
                                    f"The question: {form_field.label}\n"
                                    f"Local answer: {answer}")

                    else:
                        res, answer = self.llm_client.answer_freely(form_field.label)
                        if not res:
                            self.error_message = (f"LLM did not produce answer.\n"
                                                  f"Question was: {form_field.label}")
                            return False

                    BrowserClient.set_input_field(form_field.element, answer)

                    # In a text input field a suggestions list can appear, check every time
                    (suggestions_element,
                     suggestions_options) = self.browser_client.is_suggestions_list_appeared()

                    if suggestions_element is not None:
                        res, answer = self.llm_client.answer_with_options(form_field.label, suggestions_options)
                        if not res:
                            self.error_message = (f"LLM did not produce answer.\n"
                                                  f"Question was: {form_field.label}")
                            return False

                        self.browser_client.set_suggestions_list(suggestions_element, answer)

                case FieldTypeEnum.UPLOAD_CV:
                    resume_path = self.__get_local_resume_path_by_title()
                    if not resume_path:
                        # TODO: Generate resume with AI here
                        self.error_message = "Resume generation not implemented yet!"
                        return False

                    BrowserClient.upload_file(form_field.element, resume_path)

                case FieldTypeEnum.UPLOAD_COVER:
                    self.error_message = "Cover letter upload not implemented yet!"
                    return False

                case FieldTypeEnum.CARDS:
                    logger.info("Cards page, skipping")

                case FieldTypeEnum.CHECKBOX:
                    answer = self.__try_no_llm_answer(form_field.type, form_field.label, form_field.data)
                    if answer:
                        logger.info("Saved a cent!\n"
                                    f"The question: {form_field.label}\n"
                                    f"Local answer: {answer}")

                    else:
                        res, answer = self.llm_client.answer_with_options(form_field.label, form_field.data)
                        if not res:
                            self.error_message = (f"LLM did not produce answer.\n"
                                                  f"Question was: {form_field.label}")
                            return False

                    BrowserClient.set_checkbox_field(form_field.element)

                case _:
                    self.error_message = f"LinkedIn client got field type it doesn't recognize ({form_field.type})"
                    return False

        return True

    def start(self) -> None:
        self.browser_client.initialize()

        search_url_list = self.browser_client.make_search_urls()

        if search_url_list:
            for search_url in search_url_list:
                # Page loop
                while True:
                    job_generator = self.browser_client.get_page_jobs(search_url, self.current_page)
                    if job_generator is None:
                        break
                    # Jobs on page loop
                    while True:
                        try:
                            self.current_job = job_generator.__next__()
                            if self.current_job is None:
                                break
                            if self.current_job.applied:
                                logger.info("Already applied, skipping")
                                continue
                            if self.__is_title_or_company_blacklisted():
                                continue

                            self.browser_client.get_job_description_and_hiring_team(self.current_job)

                            form_element = self.browser_client.get_easy_apply_form()

                            if not self.__apply_to_job(form_element):
                                exception_data = (
                                    EasyApplyExceptionData(job_title=self.current_job.title,
                                                           job_link=self.current_job.link,
                                                           reason=self.error_message))
                                raise EasyApplyException(exception_data.reason, exception_data)

                            self.browser_client.finalize_easy_apply()

                            self.custom_logger.log_success(self.current_job)

                            wait_extra(extra_range_sec=NEXT_JOB_APPLICATION_DELAY)

                        except EasyApplyException as ex:
                            self.custom_logger.log_error(ex.data)
                            logger.error("Easy Apply failed!\n"
                                         f"Reason: {ex.data.reason}")
                            # If bail out fails - everything fails and bot dies :)
                            self.browser_client.bail_out()
                            continue

                    # Advance page
                    self.current_page += 1
                    wait_extra(extra_range_sec=NEXT_SEARCH_PAGE_DELAY)
                    logger.info("Advancing to page {}".format(self.current_page + 1))

                self.current_page = 0
                wait_extra(extra_range_sec=NEXT_SEARCH_DELAY)
                logger.info("Advancing to next search")
        else:
            logger.error("Can't construct a single search url!")
            return None
