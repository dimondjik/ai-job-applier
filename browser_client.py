from selenium import webdriver
from selenium_stealth import stealth
import os
from config_manager import ConfigManager
import logging
from utils import wait_extra
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from collections import OrderedDict
from urllib.parse import urlencode
from typing import Generator
from custom_types.job import Job
from custom_types.field import Field, FieldTypeEnum
import random

from custom_exceptions import (LoginFailException,
                               JobListException,
                               EasyApplyException,
                               EasyApplyExceptionData)

logger = logging.getLogger("BrowserClient")

# Dicts to convert human-readable values to query string values when filtering
# ----------------------------------------------------------------------------------------------------------------------
EXPERIENCE_LEVEL = {"internship": 1,
                    "entry_level": 2,
                    "associate": 3,
                    "mid_senior_level": 4,
                    "director": 5,
                    "executive": 6}

INDUSTRY = {"computer_games": "109",
            "software_development": "4",
            "it_services_and_it_consulting": "96"}

DATE = {"month": "r2592000",
        "week": "r604800",
        "day": "r86400"}

REMOTE = {"on_site": 1,
          "remote": 2,
          "hybrid": 3}

JOB_TYPE = {"full_time": "F",
            "part_time": "P",
            "contract": "C",
            "temporary": "T",
            "volunteer": "V",
            "internship": "I",
            "other": "O"}
# ----------------------------------------------------------------------------------------------------------------------

SCROLL_DELAY = (2., 4.)

JOB_LIST_LOAD_TIMEOUT = 8
JOB_LIST_RETRY_DELAY = (1., 2.)
JOB_LIST_CLICK_DELAY = (1., 2.)

EASY_APPLY_FORM_TIMEOUT = 8
EASY_APPLY_FORM_DELAY = (1., 2.)

EASY_APPLY_FIELD_CHECK_DELAY = (1., 2.)
EASY_APPLY_FIELD_INPUT_DELAY = (1., 2.)
EASY_APPLY_FIELD_UPLOAD_DELAY = (4., 6.)

EASY_APPLY_SUGGESTION_BOX_TIMEOUT = 3

EASY_APPLY_SUBMIT_FINAL_DELAY = (4., 6.)
EASY_APPLY_SUBMIT_STEP_DELAY = (2., 4.)
EASY_APPLY_POPUP_DETECT_TIMEOUT = 6

BAIL_OUT_STEP_DELAY = (2., 4.)


class BrowserClient:
    def __init__(self):
        """
        Class for browser manipulation, tailored for LinkedIn site

        Will initialize Web Driver, and launch Chrome if everything succeeded
        """

        # TODO: Catch error when browser failed to initialize

        self.config = ConfigManager()

        # Pointing Chrome data in current working directory
        self.chrome_folder = os.path.join(os.getcwd(), "chrome_data")
        self.profile_folder = os.path.join(os.getcwd(), "chrome_data", "linkedin_profile")
        self.__create_profile_folder()

        # Making options object
        options = webdriver.ChromeOptions()
        # Chrome options
        # --------------------------------------------------------------------------------------------------------------
        options.add_argument("start-maximized")
        # Pretty dangerous?
        # options.add_argument("no-sandbox")
        # options.add_argument("ignore-certificate-errors")
        options.add_argument("disable-extensions")
        options.add_argument("disable-gpu")
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("disable-blink-features")
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(f"user-data-dir={self.chrome_folder}")
        options.add_argument(f"profile-directory={os.path.basename(self.profile_folder)}")
        # --------------------------------------------------------------------------------------------------------------
        # Webdriver object
        self.driver = webdriver.Chrome(options=options)
        # Webdriver stealth wrapper with default parameters
        stealth(self.driver,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "  # noqa
                           "Chrome/83.0.4103.53 Safari/537.36",
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win64",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=False)

        self.actions = ActionChains(self.driver)

        self.__logged_in = False

        # Mainly for logging purposes
        self.current_job = None

        logger.info("Chrome driver created")

    def __create_profile_folder(self) -> None:
        """
        Create separate profile folder for selenium chrome session
        """
        if not os.path.exists(self.chrome_folder):
            os.mkdir(self.chrome_folder)
        if not os.path.exists(self.profile_folder):
            os.mkdir(self.profile_folder)

    def make_search_urls(self) -> list[str]:
        """
        Generate list of search queries based on filters.yaml

        Links in the list are in random order

        :return: Search links
        """
        # LinkedIn search url query cheatsheet
        # --------------------------------------------------------------------------------------------------------------
        # Title filter:
        # keywords=example job
        # https://www.linkedin.com/jobs/search/?keywords=gameplay developer  # noqa

        # Date filter:
        # f_TPR=r86400

        # Values (Single value):
        # Month = r2592000
        # Week = r604800
        # Day = r86400
        # Any time = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_TPR=r86400&keywords=gameplay developer  # noqa

        # Experience level filter:
        # f_E=2,3,4
        # f_E=2

        # Values (Multiple values):
        # Internship = 1
        # Entry level = 2
        # Associate = 3
        # Mid-Senior level = 4
        # Director = 5
        # Executive = 6
        # Any = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_E=2,3,4&f_TPR=r86400&keywords=gameplay developer  # noqa

        # Remote filter:
        # f_WT=1,2,3
        # f_WT=1

        # Values (Multiple values):
        # On-site = 1
        # Remote = 2
        # Hybrid = 3
        # Any = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_E=2,3,4&f_TPR=r86400&f_WT=2&keywords=gameplay developer  # noqa

        # Easy apply filter:
        # f_AL=true

        # Values (Single value):
        # Easy apply = true
        # No easy apply = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2,3,4&f_TPR=r86400&f_WT=2&keywords=gameplay developer  # noqa

        # Location filter (Single value):
        # location=Example

        # Values:
        # Type in existing country :)

        # https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2,3,4&f_TPR=r86400&f_WT=2&location=Canada&keywords=gameplay developer  # noqa

        # Industry filter (Multiple values):
        # f_I=109,4

        # Values (Incomplete list) (Multiple values):
        # Computer Games = 109
        # Software Development = 4
        # IT Services and IT Consulting = 96
        # Any = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2,3,4&f_I=109,4&f_TPR=r86400&f_WT=2&location=Canada&keywords=gameplay developer  # noqa

        # Job type filter (Multiple values):
        # f_JT=F,P,C,T,V,I,O

        # Values (Multiple values):
        # Full-time = F
        # Part-time = P
        # Contract = C
        # Temporary = T
        # Volunteer = V
        # Internship = I
        # Other = O
        # Any = Remove the filter

        # https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2,3,4&f_I=109,4&f_TPR=r86400&f_WT=2&location=Canada&keywords=gameplay developer  # noqa

        # Order: easy apply, experience level, industry, job type, date, remote, location, title
        # --------------------------------------------------------------------------------------------------------------

        # TODO: Slow? Multiple access to config, which is reloading every time field is accessed?
        title_location_pairs = ([location, title] for location in self.config.location for title in self.config.title)

        search_link_list = []

        for pair in title_location_pairs:
            query_url = "https://www.linkedin.com/jobs/search/?"
            query_dict = OrderedDict(f_AL=True,
                                     # This monstrous one-liner is:
                                     # For every key and item in yaml dict "experience_level"
                                     # - for k, v in self.config.experience_level.items()
                                     # If value is True - translate it to query value and append to list, else - nothing
                                     # - EXPERIENCE_LEVEL[k] if v else ""
                                     # Then join that list into string
                                     # - "".join([list from generator])
                                     # Then remove trailing comma
                                     # - [:-1]
                                     # Going to be the same for other keys
                                     f_E="".join(["{},".format(EXPERIENCE_LEVEL[k]) if v else ""
                                                  for k, v in self.config.experience_level.items()])[:-1],
                                     f_I="".join(["{},".format(INDUSTRY[k]) if v else ""
                                                  for k, v in self.config.industry.items()])[:-1],
                                     f_JT="".join(["{},".format(JOB_TYPE[k]) if v else ""
                                                   for k, v in self.config.job_type.items()])[:-1],
                                     f_TPR="".join(["{},".format(DATE[k]) if v else ""
                                                    for k, v in self.config.date.items()])[:-1],
                                     f_WT="".join(["{},".format(REMOTE[k]) if v else ""
                                                   for k, v in self.config.remote.items()])[:-1],
                                     location=pair[0],
                                     keywords=pair[1])

            query_url += urlencode(query_dict)
            search_link_list.append(query_url)

        random.shuffle(search_link_list)

        return search_link_list

    def __linkedin_log_in(self) -> None:
        """
        Login into LinkedIn using credentials from secrets.yaml

        MUST be called on login page!
        """

        try:
            sign_in_button = self.driver.find_element(By.XPATH, "//button[@aria-label=\"Sign in\"]")
        except NoSuchElementException:
            raise LoginFailException(
                "Login function called on non-login page ({})".format(self.driver.current_url))

        try:
            email_field = self.driver.find_element(By.XPATH, "//input[@id=\"username\"]")
            email_field.send_keys(self.config.linkedin_email)
            wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)
        except NoSuchElementException:
            logger.info("Can't find \"Email or phone\" field. Assuming only password is needed")

        try:
            password_field = self.driver.find_element(By.XPATH, "//input[@id=\"password\"]")
            password_field.send_keys(self.config.linkedin_pass)
            wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)
        except NoSuchElementException:
            raise LoginFailException(
                "Can't find \"Password\" field ({})".format(self.driver.current_url))

        sign_in_button.click()
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    def initialize(self) -> None:
        """
        Open LinkedIn feed, the starting point for bot

        Will autologin if not logged in yet

        :return: Result of initialization
        """
        logger.debug("Opening linkedin feed")
        self.driver.get("https://www.linkedin.com/feed/")
        wait_extra()

        if not self.__logged_in:
            if self.driver.current_url != "https://www.linkedin.com/feed/":
                logger.info("Not logged in")
                self.__linkedin_log_in()
                self.__logged_in = True
                logger.info("Logged in!")
            else:
                self.__logged_in = True
                logger.info("Already logged in!")
        else:
            logger.info("Already logged in!")

    def __scroll_to_element(self, element: WebElement) -> None:
        """
        Scroll do desired element

        Plus some wait to let the element load

        :param element: desired element
        """
        if element.is_displayed():
            logger.debug("Element already visible")
        else:
            logger.debug("Scrolling to an element")
            self.actions.scroll_to_element(element).perform()
            # Let the element load
            wait_extra(extra_range_sec=SCROLL_DELAY)

    def __get_jobs_list(self, max_retries: int = 3) -> list[WebElement]:
        """
        Get job items on page, retry until two list lengths will be equal (to let all entries on the layout to load)

        :param max_retries: Max retries to compare list lengths

        :return: List of job entry elements
        """
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

        logger.debug("Getting job list")

        try:
            prev_jobs_count = len(WebDriverWait(self.driver,
                                                JOB_LIST_LOAD_TIMEOUT,
                                                ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_all_elements_located((By.XPATH,
                                                       "//div[contains(@class, "
                                                       "\"jobs-search-results-list\")]"
                                                       "/ul[contains(@class, "
                                                       "\"scaffold-layout__list-container\")]"
                                                       "/li[contains(@class, "
                                                       "\"jobs-search-results__list-item\")]"))))
        except TimeoutException:
            raise JobListException(
                "Job search result list not found ({})"
                .format(self.driver.current_url))

        retries = 0

        while retries < max_retries:
            wait_extra(extra_range_sec=JOB_LIST_RETRY_DELAY)

            try:
                jobs_list = WebDriverWait(self.driver,
                                          JOB_LIST_LOAD_TIMEOUT,
                                          ignored_exceptions=ignored_exceptions).until(
                    ec.visibility_of_all_elements_located((By.XPATH,
                                                           "//div[contains(@class, "
                                                           "\"jobs-search-results-list\")]"
                                                           "/ul[contains(@class, "
                                                           "\"scaffold-layout__list-container\")]"
                                                           "/li[contains(@class, "
                                                           "\"jobs-search-results__list-item\")]")))
            except TimeoutException:
                raise JobListException(
                    "Job search result list not found ({})"
                    .format(self.driver.current_url))

            if len(jobs_list) == prev_jobs_count:
                return jobs_list
            else:
                logger.debug(f"Job list lengths are not equal ({retries + 1})")
                prev_jobs_count = len(jobs_list)
                retries += 1

        logger.warning(f"Job list lengths comparing retries exceeded max_retries ({max_retries})!")
        return []

    def get_jobs_from_search_url(self, url: str) -> Generator[Job | None, None, None]:
        """
        Get data from jobs list on the search url

        :param url: Search url, should contain element with class "jobs-search-results-list"

        :return: Job object with info from the page
        """
        # Go to search page with provided link
        self.driver.get(url)
        logger.info(f"Searching {url}")

        try:
            # Try to find no jobs banner, if not found and exception thrown - that's great,
            # means that something is found
            self.driver.find_element(By.CLASS_NAME, "jobs-search-no-results-banner")
            logger.info("No jobs found")
            yield None
        except NoSuchElementException:
            pass

        jobs_count = len(self.__get_jobs_list())

        logger.info(f"Jobs on page: {jobs_count}")

        for i in range(jobs_count):
            # Double getting job items, since when we scroll some elements go stale,
            # because they are updated with job info by the website

            # TODO: Removed second check, hope that LinkedIn would give info about next job in time

            job_item = self.__get_jobs_list()[i]

            self.__scroll_to_element(job_item)

            # job_item = self.__get_jobs_list()[i]

            logger.debug("Clicked on the job in the list")

            # Click on job item
            self.actions.click(job_item).perform()

            # Let the right bar load
            wait_extra(extra_range_sec=JOB_LIST_CLICK_DELAY)

            try:
                # Don't really need another variable, this is just for logging purposes
                job_data = Job(title=job_item.find_element(By.XPATH,
                                                           ".//a[contains(@class, \"job-card-list__title\")]"
                                                           ).get_attribute("aria-label"),
                               company=job_item.find_element(By.XPATH,
                                                             ".//span[contains(@class, "
                                                             "\"job-card-container__primary-description\")]"
                                                             ).text,
                               location=job_item.find_element(By.XPATH,
                                                              ".//li[contains(@class, "
                                                              "\"job-card-container__metadata-item\")]"
                                                              ).text,
                               link=job_item.find_element(By.XPATH,
                                                          ".//a[contains(@class, \"job-card-list__title\")]"
                                                          ).get_attribute("href"))

                try:
                    job_data.applied = (True if job_item.find_element(
                        By.XPATH,
                        ".//li[contains(@class, \"job-card-container__footer-job-state\")]").text == "Applied"
                                        else False)
                except NoSuchElementException:
                    job_data.applied = False

            except NoSuchElementException:
                raise JobListException("Cannot get job info ({})".format(self.driver.current_url))

            logger.info(f"Found job item: {job_data.title} ({job_data.company})")

            # Mainly for logging purposes
            self.current_job = job_data

            yield job_data

        yield None

    def get_job_description_and_hiring_team(self, job_data: Job) -> None:
        """
        Expand job_data dictionary with additional data:

        - Job description

        - Link to hiring team (usually one person LinkedIn link)

        MUST BE CALLED ON SEARCH PAGE WITH FULLY LOADED RIGHT BAR

        :param job_data: Job object to expand
        """

        logger.debug("Adding description and HR link to Job object")

        try:
            job_data.desc = self.driver.find_element(
                By.XPATH, "//article[contains(@class, \"jobs-description__container\")]").text
        except NoSuchElementException:
            raise JobListException("Can't find job description ({})".format(self.current_job.link))

        try:
            job_data.hr = self.driver.find_element(
                By.XPATH, "//div[contains(@class, \"hirer-card__hirer-information\")]"
                          "/a[contains(@href, \"https://www.linkedin.com/\")]").get_attribute("href")
        except NoSuchElementException:
            logger.debug("Can't find HR link, that's not essential")
            pass

        # Mainly for logging purposes
        self.current_job = job_data

    def __advance_easy_apply_form(self) -> WebElement | None:
        """
        Advance the form and return new form element

        :return: Form element
        """
        try:
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

            self.actions.click(
                self.driver.find_element(
                    By.XPATH, "//button[contains(@aria-label, \"Continue to next step\") "
                              "and ./span[contains(., \"Next\")]]")).perform()

            form_element = WebDriverWait(self.driver, EASY_APPLY_FORM_TIMEOUT,
                                         ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, \"jobs-easy-apply-modal\")]")))

            logger.info("Advancing the Easy Apply form")

            wait_extra(extra_range_sec=EASY_APPLY_FORM_DELAY)

            return form_element

        except NoSuchElementException:
            return None

    def finalize_easy_apply(self) -> None:
        """
        Finalize job application, call this function at the last step when Review button appear
        """
        try:
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

            # Click Review button
            next_button = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, \"Review your application\") "
                          "and ./span[contains(., \"Review\")]]")
            self.__scroll_to_element(next_button)
            self.actions.click(next_button).perform()

            WebDriverWait(self.driver, EASY_APPLY_FORM_TIMEOUT,
                          ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, \"jobs-easy-apply-modal\")]")))

            wait_extra(extra_range_sec=EASY_APPLY_SUBMIT_STEP_DELAY)

            # Unfollow company
            next_button = self.driver.find_element(
                By.XPATH, "//input[@id=\"follow-company-checkbox\" and @type=\"checkbox\"]")
            self.__scroll_to_element(next_button)
            self.actions.click(next_button).perform()

            wait_extra(extra_range_sec=EASY_APPLY_SUBMIT_STEP_DELAY)

            # Submit
            next_button = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, \"Submit application\") "
                          "and ./span[contains(., \"Submit application\")]]")
            self.__scroll_to_element(next_button)
            self.actions.click(next_button).perform()

            # Wait for something to pop up
            wait_extra(extra_range_sec=EASY_APPLY_SUBMIT_FINAL_DELAY)

            try:
                # Wait for something to pop up of a dialog class
                any_dialog = WebDriverWait(self.driver, EASY_APPLY_POPUP_DETECT_TIMEOUT,
                                           ignored_exceptions=ignored_exceptions).until(
                    ec.visibility_of_element_located((By.XPATH, "//div[@role=\"dialog\"]")))

                # Closing popup dialog
                self.actions.click(
                    any_dialog.find_element(
                        By.XPATH, ".//button[@aria-label=\"Dismiss\"]")).perform()

                logger.info("Successfully closed popup")
            except TimeoutException:
                pass

            logger.info(f"Successful {self.current_job.title} application at {self.current_job.company}!")

            wait_extra(extra_range_sec=EASY_APPLY_SUBMIT_STEP_DELAY)

        except NoSuchElementException:
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="Can't finalize Easy Apply")
            raise EasyApplyException("Can't finalize Easy Apply", exception_data)

    def bail_out(self):
        try:
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

            # Find form element
            form_element = WebDriverWait(self.driver, EASY_APPLY_FORM_TIMEOUT,
                                         ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, \"jobs-easy-apply-modal\")]")))

            # Closing form
            self.actions.click(
                form_element.find_element(
                    By.XPATH, ".//button[@aria-label=\"Dismiss\"]")).perform()

            wait_extra(extra_range_sec=BAIL_OUT_STEP_DELAY)

            # Find save application dialog
            save_dialog = WebDriverWait(self.driver, EASY_APPLY_POPUP_DETECT_TIMEOUT,
                                        ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, "//div[@role=\"alertdialog\"]")))

            # Discard application
            self.actions.click(
                save_dialog.find_element(
                    By.XPATH, ".//button[./span[text()[contains(., \"Discard\")]]]")).perform()

            wait_extra(extra_range_sec=BAIL_OUT_STEP_DELAY)
        except NoSuchElementException:
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="Can't close Easy Apply form...")
            raise EasyApplyException("Can't close Easy Apply form...", exception_data)

    def get_easy_apply_form(self) -> WebElement:
        """
        Locate and click Easy Apply button on this page

        :return: Form element
        """

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

        logger.info("Opening the Easy Apply form")

        try:
            self.actions.click(
                self.driver.find_element(
                    By.XPATH,
                    "//button[contains(@class, \"jobs-apply-button\") "
                    "and ./span[contains(., \"Easy Apply\")]]")).perform()
        except NoSuchElementException:
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="No Easy Apply button")
            raise EasyApplyException("Can't find Easy Apply button", exception_data)

        try:
            form_element = WebDriverWait(self.driver,
                                         EASY_APPLY_FORM_TIMEOUT,
                                         ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, "//div[contains(@class, \"jobs-easy-apply-modal\")]")))
        except TimeoutException:
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="No Easy Apply form")
            raise EasyApplyException("Can't find Easy Apply form", exception_data)

        wait_extra(extra_range_sec=EASY_APPLY_FORM_DELAY)

        return form_element

    def __get_label_from_field_element(self, field_element: WebElement) -> str:
        """
        Get label of the field

        :param field_element: Form field element
        :return: Label string
        """
        # TODO: List element is a problem, when there's really long labels (happens from time to time, yes)
        #  Same thing for checkboxes, culprit is two spans with class="visually-hidden" and aria-hidden=true
        #  Not sure which one to use

        # Trying to get label with class usually used for text input
        try:
            return field_element.find_element(
                By.XPATH, ".//label[contains(@class, \"artdeco-text-input--label\")]").text  # noqa
        except NoSuchElementException:
            pass

        # Trying to get label with class usually used for list input
        try:
            return field_element.find_element(
                By.XPATH, ".//label[contains(@class, \"fb-dash-form-element__label\")]").text
        except NoSuchElementException:
            pass

        # Why? Just WHY?
        # Trying to get label, which is actually a title outside form element group
        try:
            return field_element.find_element(
                By.XPATH, "../../span[contains(@class, \"jobs-easy-apply-form-section__group-title\")]").text
        except NoSuchElementException:
            pass

        # Trying to get label with class usually used for checkboxes
        try:
            return field_element.find_element(
                By.XPATH, ".//div[contains(@class, \"fb-dash-form-element__label\")]").text
        except NoSuchElementException:
            pass

        # Trying to get label with class usually used for radio buttons input
        try:
            return field_element.find_element(
                By.XPATH, ".//span[contains(@class, \"fb-dash-form-element__label\")]").text
        except NoSuchElementException:
            # We tried every type yet known, throw exception
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="Can't find Easy Apply form field's label")
            raise EasyApplyException("Can't find Easy Apply form field's label", exception_data)

            # Wait I have another idea
            # # Now I don't think label exception rise is alright, because we have CARDS now! My god...
            # # We tried every type yet known, return nothing
            # return ""

    def __get_data_from_field_element(self, field_element: WebElement) -> tuple[WebElement,
                                                                                FieldTypeEnum,
                                                                                list[str] | None]:
        """
        Get data about the field:
        actual web element, type from known ones, additional data e.g. options if that's a list

        :param field_element: Form field element
        :return: Field input element, type and additional data
        """
        try:
            # Is this a list? Trying to find list
            element = field_element.find_element(By.XPATH, ".//select")
            field_type = FieldTypeEnum.LIST
            field_data = [o.get_attribute("value") for o in
                          field_element.find_elements(By.XPATH, ".//select/option")]

            return element, field_type, field_data
        except NoSuchElementException:
            pass

        try:
            # Is this a text input field? Trying to find text input
            element = field_element.find_element(By.XPATH, ".//input[@type=\"text\"]")
            field_type = FieldTypeEnum.INPUT
            field_data = None

            return element, field_type, field_data
        except NoSuchElementException:
            pass

        try:
            # Is this a textarea input field? Trying to find text input
            element = field_element.find_element(By.XPATH, ".//textarea")
            field_type = FieldTypeEnum.INPUT
            field_data = None

            return element, field_type, field_data
        except NoSuchElementException:
            pass

        try:
            # Is this a checkbox? Trying to find checkbox
            checkbox = field_element.find_element(By.XPATH, ".//input[@type=\"checkbox\"]")
            element = field_element
            field_type = FieldTypeEnum.CHECKBOX
            # Hack to make checkbox an options containing element :)
            field_data = [checkbox.find_element(By.XPATH, "../label").text]

            return element, field_type, field_data
        except NoSuchElementException:
            pass

        try:
            # Is this a radio button? Trying to find radio field
            radio = field_element.find_elements(By.XPATH, ".//input[@type=\"radio\"]")
            element = field_element
            field_type = FieldTypeEnum.RADIO
            field_data = [r.find_element(By.XPATH, "../label").text for r in radio]

            return element, field_type, field_data
        except NoSuchElementException:
            # We tried every type yet known, throw exception
            exception_data = EasyApplyExceptionData(job_title=self.current_job.title,
                                                    job_link=self.current_job.link,
                                                    reason="Can't find Easy Apply form field")
            raise EasyApplyException("Can't find Easy Apply form field", exception_data)

    def __get_upload_fields_data(self, form_element: WebElement) -> list[Field]:
        try:
            upload_elements = form_element.find_elements(By.XPATH, ".//div[./input[@type=\"file\"]]")

            upload_fields = []

            for element in upload_elements:
                element_data = Field()
                element_data.label = element.text

                # Cutting edge of type determining technology!
                if element_data.label.lower().find("resume") != -1:
                    element_data.type = FieldTypeEnum.UPLOAD_CV
                elif element_data.label.lower().find("cover letter") != -1:
                    element_data.type = FieldTypeEnum.UPLOAD_COVER
                else:
                    # TODO: Is it always safe to skip?
                    continue

                element_data.element = element.find_element(By.XPATH, ".//input[@type=\"file\"]")
                upload_fields.append(element_data)

            return upload_fields

        except NoSuchElementException:
            return []

    def get_form_fields(self, form_element: WebElement) -> Generator[Field | None, None, None]:
        """
        Getting field label, type and additional data (e.g. if that's a list)

        :param form_element: Form element to breakdown
        :return: Form Field object
        """

        # TODO: Interesting consequence of this approach is that
        #  it will skip page comprised of unknown fields possibly breaking everything, rethink that
        while True:
            # Find form elements
            easy_apply_form_fields = form_element.find_elements(
                By.XPATH, "//div[contains(@class, \"jobs-easy-apply-form-element\")]")

            # If found any input fields
            if easy_apply_form_fields:
                for form_field in easy_apply_form_fields:
                    field_data = Field()

                    wait_extra(extra_range_sec=EASY_APPLY_FIELD_CHECK_DELAY)

                    field_data.label = self.__get_label_from_field_element(form_field)

                    (field_data.element,
                     field_data.type,
                     field_data.data) = self.__get_data_from_field_element(form_field)

                    yield field_data

            # Assuming we need to upload something
            # Not through "else" with operator above, because there's pages with upload AND some input fields
            # TODO: Inconsistency with approach above where data returned separately and then packed into object?
            #  A) Leave as it is to not make nested generator
            #  B) Remake above approach to return object (preferred)
            upload_fields = self.__get_upload_fields_data(form_element)

            # If found upload fields
            if upload_fields:
                for upload_field in upload_fields:
                    yield upload_field

            # If not assuming that's cards page, as far as I know it has unique container
            else:
                try:
                    form_element.find_element(
                        By.XPATH, ".//form["
                                  "./div[contains(@class, \"jobs-easy-apply-repeatable-groupings__groupings\")]]")
                    field_data = Field()
                    field_data.type = FieldTypeEnum.CARDS
                    yield field_data
                except NoSuchElementException:
                    pass

            # Seamless form advancing
            form_element = self.__advance_easy_apply_form()

            # If we can't advance further, it should be stopped here on the caller's side
            if form_element is None:
                yield None

    @staticmethod
    def set_input_field(input_field: WebElement, value: str) -> None:
        """
        Send keys to WebElement, assuming that is a text input field

        Fire and pray :)

        :param input_field: Text input field
        :param value: Value to insert
        """
        input_field.send_keys(Keys.CONTROL + 'a')
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)
        input_field.send_keys(Keys.DELETE)
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)
        input_field.send_keys(value)
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    @staticmethod
    def set_dropdown_field(dropdown_field: WebElement, value: str) -> None:
        """
        Select element from WebElement, assuming that is a dropdown field, with corresponding value

        Fire and pray :)

        :param dropdown_field: Dropdown field element
        :param value: Visible text in dropdown to select
        """
        select_driver = Select(dropdown_field)
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)
        select_driver.select_by_visible_text(value)
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    @staticmethod
    def upload_file(upload_field: WebElement, abspath: str) -> None:
        """
        Upload file to upload element

        Fire and pray :)

        :param upload_field: Invisible input WebElement for upload
        :param abspath: Absolute path to uploading file
        """
        upload_field.send_keys(abspath)
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_UPLOAD_DELAY)

    @staticmethod
    def set_radio_field(radio_field: WebElement, value: str) -> None:
        """
        Click element from WebElement, assuming that is radio buttons container, with corresponding value

        Fire and pray :)

        :param radio_field: Radio buttons field container element
        :param value: Visible text on radio button to select
        """

        # TODO: Selenium doesnt want to click on input element, try with Actions.click.perform instead?
        #  input field is underneath label on LinkedIn
        # radio_field.find_element(By.XPATH, f".//input[@type=\"radio\" and @value=\"{value}\"]").click()
        radio_field.find_element(By.XPATH, f".//label[text()[contains(., \"{value}\")]]").click()
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    @staticmethod
    def set_checkbox_field(checkbox_field: WebElement, value: str) -> None:
        """
        Click element from WebElement, assuming that is checkbox container, with corresponding value

        Fire and pray :)

        :param checkbox_field: Radio buttons field container element
        :param value: Visible text on radio button to select
        """

        # TODO: Selenium doesnt want to click on input element, try with Actions.click.perform instead?
        #  input field is underneath label on LinkedIn
        # radio_field.find_element(By.XPATH, f".//input[@type=\"radio\" and @value=\"{value}\"]").click()
        checkbox_field.find_element(By.XPATH, f".//label[text()[contains(., \"{value}\")]]").click()
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    def set_suggestions_list(self, suggestions_element: WebElement, value: str) -> None:
        """
        Setting text input suggestions list value

        Fire and pray :)

        :param suggestions_element: suggestions list web element
        :param value: value to set
        """

        target_element = suggestions_element.find_element(By.XPATH,
                                                          f".//div[@role=\"option\" and "
                                                          f".//span[text()[contains(., \"{value}\")]]]")
        self.__scroll_to_element(target_element)
        self.actions.click(target_element).perform()
        wait_extra(extra_range_sec=EASY_APPLY_FIELD_INPUT_DELAY)

    def is_suggestions_list_appeared(self) -> tuple[WebElement | None, list[str] | None]:
        """
        Check if suggestions element appeared, usually after input in text field

        :return: None if no suggestions list, otherwise - suggestions element and options
        """

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

        try:
            suggestions_element = WebDriverWait(self.driver,
                                                EASY_APPLY_SUGGESTION_BOX_TIMEOUT,
                                                ignored_exceptions=ignored_exceptions).until(
                ec.visibility_of_element_located((By.XPATH, ".//div[@role=\"listbox\" and .//div[@role=\"option\"]]")))
        except TimeoutException:
            logger.debug("Suggestions not found")
            return None, None

        logger.info("Suggestions appeared")
        suggestions_options = [o.text for o in
                               suggestions_element.find_elements(By.XPATH, ".//div[@role=\"option\"]")]

        return suggestions_element, suggestions_options
