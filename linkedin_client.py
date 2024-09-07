from browser_client import BrowserClient
from config_manager import ConfigManager
from utils import wait_extra


class LinkedInClient:
    def __init__(self):
        self.browser_client = BrowserClient()
        self.config = ConfigManager()

    def start(self):
        self.browser_client.linkedin_open_feed()
        search_url_list = self.browser_client.make_search_urls()
        for search_url in search_url_list:
            for job in self.browser_client.get_jobs_from_search_url(search_url):
                print(job)
        wait_extra()
