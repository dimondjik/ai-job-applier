from selenium import webdriver
from selenium_stealth import stealth
import os
from config_manager import ConfigManager
import logging
from utils import wait_extra
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from collections import OrderedDict
from urllib.parse import urlencode
import random

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

# SCROLL_DELAY_RANGE = (1., 2.)

JOB_LIST_LOAD_TIMEOUT = 8
JOB_LIST_RETRY_DELAY_RANGE = (1., 2.)

JOB_CLICK_DELAY = (1., 2.)


class BrowserClient:
    def __init__(self):
        """
        Class for browser manipulation, tailored for LinkedIn site

        Will initialize selenium stealth, and launch chrome if everything succeeded
        """
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

    def __create_profile_folder(self):
        """
        Create separate profile folder for selenium chrome session
        """
        if not os.path.exists(self.chrome_folder):
            os.mkdir(self.chrome_folder)
        if not os.path.exists(self.profile_folder):
            os.mkdir(self.profile_folder)

    def make_search_urls(self):
        """
        Generate list of search queries based on filters.yaml. Links are in random order

        :return: List of search url's
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

        # Slow? Multiple access to config, which is reloading every time field is accessed?
        title_location_pairs = [[location, title] for location in self.config.location for title in self.config.title]
        random.shuffle(title_location_pairs)

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

        # Another shuffle just in case :)
        random.shuffle(search_link_list)

        return search_link_list

    def __linkedin_log_in(self):
        """
        Login into LinkedIn using credentials from secrets.yaml

        MUST be called on login page!

        :return: True if logged in, False if something went wrong
        """
        logger.info("Checking if that's the login page")
        try:
            sign_in_button = self.driver.find_element(By.XPATH, "//button[@aria-label=\"Sign in\"]")
            logger.info("That's the login page")
        except NoSuchElementException:
            logger.error("Couldn't confirm that this is the login page!")
            return False

        logger.info("Entering credentials")
        try:
            email_field = self.driver.find_element(By.XPATH, "//input[@id=\"username\"]")
            email_field.send_keys(self.config.linkedin_email)
            wait_extra()
        except NoSuchElementException:
            logger.info("Couldn't find \"Email or phone\" field. Assuming only password needed")

        password_field = self.driver.find_element(By.XPATH, "//input[@id=\"password\"]")
        password_field.send_keys(self.config.linkedin_pass)
        wait_extra()

        sign_in_button.click()
        logger.info("Done!")
        wait_extra()
        return True

    def linkedin_open_feed(self):
        """
        Open LinkedIn feed, the starting point for bot

        Will autologin if not logged in yet

        :return: True if opened feed, False if something went wrong
        """
        logger.info("Opening linkedin feed")
        self.driver.get("https://www.linkedin.com/feed/")
        wait_extra()

        if not self.__logged_in:
            if self.driver.current_url != "https://www.linkedin.com/feed/":
                logger.info("We have been redirected")
                logger.info("Assuming that is the login page")
                if not self.__linkedin_log_in():
                    logger.error("Redirected to somewhere else from the feed when not logged in!")
                    return False
                else:
                    self.__logged_in = True
                    logger.info("Logged in!")
            else:
                self.__logged_in = True
                logger.info("Already logged in!")
        else:
            logger.info("Already logged in!")

        return True

    def __scroll_to_element(self, element):
        """
        Scroll do desired element

        (As of now - no delay, leaving just in case it appears again, ignore next sentence)

        Plus some wait to let the element load

        :param element: desired element
        """
        self.actions.scroll_to_element(element).perform()
        # Does it really need a delay? Since we have delay in __get_job_items
        # # Let the element load
        # wait_extra(extra_range_sec=SCROLL_DELAY_RANGE)

    def __get_job_items(self, max_retries=3):
        """
        Get job items on page, retry until two list lengths will be equal (to let all entries on the layout to load)
        :param max_retries: max retries to compare list lengths

        :return: List of job entry elements, empty list if something is wrong
        """
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
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
        retries = 0

        while retries < max_retries:
            wait_extra(extra_range_sec=JOB_LIST_RETRY_DELAY_RANGE)
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

            if len(jobs_list) == prev_jobs_count:
                return jobs_list
            else:
                logger.info(f"Job list lengths are not equal, retrying ({retries + 1})...")
                prev_jobs_count = len(jobs_list)
                retries += 1

        logger.warning(f"Job list lengths comparing retries exceeded max_retries ({max_retries})!")
        return []

    def get_jobs_from_search_url(self, url):
        """
        Get data from jobs list on the search url

        THIS IS A GENERATOR FUNCTION!

        :param url: Search url, should contain element with class "jobs-search-results-list"
        :return: Single job element, get next one with explicit or implicit next() call
        """
        # Go to search page with provided link
        self.driver.get(url)
        logger.info(f"Searching {url}")

        try:
            # Try to find no jobs banner, if not found and exception thrown - that's great,
            # means that something is found
            self.driver.find_element(By.CLASS_NAME, "jobs-search-no-results-banner")
            logger.info("No jobs found")
            return []
        except NoSuchElementException:
            pass

        jobs_count = len(self.__get_job_items())

        logger.info(f"Jobs on page: {jobs_count}")

        # # Extracted data from jobs list
        # jobs_data = []

        for i in range(jobs_count):
            # Double getting job items, since when we scroll some elements go stale,
            # because they are updated with job info by website
            job_item = self.__get_job_items()[i]

            self.__scroll_to_element(job_item)

            job_item = self.__get_job_items()[i]

            # Click on job item
            self.actions.click(job_item).perform()

            # Let the right bar load
            wait_extra(extra_range_sec=JOB_CLICK_DELAY)

            # # Append dict to jobs list with info that we can get from the panel in jobs list element
            # jobs_data.append({"title": job_item.find_element(By.XPATH,
            #                                                  ".//a[contains(@class, \"job-card-list__title\")]"
            #                                                  ).get_attribute("aria-label"),
            #                   "link": job_item.find_element(By.XPATH,
            #                                                 ".//a[contains(@class, \"job-card-list__title\")]"
            #                                                 ).get_attribute("href"),
            #                   "company": job_item.find_element(By.XPATH,
            #                                                    ".//span[contains(@class, "
            #                                                    "\"job-card-container__primary-description\")]"
            #                                                    ).text,
            #                   "location": job_item.find_element(By.XPATH,
            #                                                     ".//li[contains(@class, "
            #                                                     "\"job-card-container__metadata-item\")]"
            #                                                     ).text})

            # Don't really need another variable, this is just for logging purposes
            job_data = {"title": job_item.find_element(By.XPATH,
                                                       ".//a[contains(@class, \"job-card-list__title\")]"
                                                       ).get_attribute("aria-label"),
                        "link": job_item.find_element(By.XPATH,
                                                      ".//a[contains(@class, \"job-card-list__title\")]"
                                                      ).get_attribute("href"),
                        "company": job_item.find_element(By.XPATH,
                                                         ".//span[contains(@class, "
                                                         "\"job-card-container__primary-description\")]"
                                                         ).text,
                        "location": job_item.find_element(By.XPATH,
                                                          ".//li[contains(@class, "
                                                          "\"job-card-container__metadata-item\")]"
                                                          ).text}

            # logger.info(f"Found job item: {jobs_data[-1]['title']} ({jobs_data[-1]['company']})")
            logger.info(f"Found job item: {job_data['title']} ({job_data['company']})")
            yield job_data

        # return jobs_data

    def get_job_description_and_hiring_team(self, job_data):
        """
        Expand job_data dictionary with additional data:
        - Job description
        - Link to hiring team (usually one person LinkedIn link)

        MUST BE CALLED ON SEARCH PAGE WITH FULLY LOADED RIGHT BAR

        :param job_data: dictionary of job_data to expand
        """

        try:
            job_data["desc"] = self.driver.find_element(
                By.XPATH, ".//article[contains(@class, \"jobs-description__container\")]").text
        except NoSuchElementException:
            logger.error("Something is completely wrong, we didn't find job description")
            raise Exception("Something is completely wrong, we didn't find job description")

        try:
            job_data["hr"] = self.driver.find_element(
                By.XPATH, ".//div[contains(@class, \"hirer-card__hirer-information\")]"
                          "/a[contains(@href, \"https://www.linkedin.com/\")]").get_attribute("href")
        except NoSuchElementException:
            logger.info("We didn't find hiring team link, skipping that")
            pass
