from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()

    time.sleep(4096)
