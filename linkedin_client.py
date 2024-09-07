from browser_client import BrowserClient
from config_manager import ConfigManager
from utils import wait_extra


class LinkedInClient:
    def __init__(self):
        self.browser_client = BrowserClient()
        self.config = ConfigManager()

    def start(self):
        self.browser_client.open_feed()
        search_url_list = self.browser_client.make_search_urls()
        for search_url in search_url_list:
            for job in self.browser_client.get_jobs_from_search_url(search_url):
                self.browser_client.get_job_description_and_hiring_team(job)
                form_element = self.browser_client.get_easy_apply_form()
                for form_field in BrowserClient.get_form_fields(form_element):
                    print(form_field)
        wait_extra()
