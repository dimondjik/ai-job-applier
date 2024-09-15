from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.INFO)

for name, logger in logging.root.manager.loggerDict.items():
    if name not in ["LinkedInClient", "LLMClient", "BrowserClient"]:
        logger.disabled = True

# TODO: Add Canada work eligibility = false, true whatever
#  Add postal code = something, numbers
#  Add cover letter...

# TODO: Job object is duplicated in linkedin and browser clients!
#  Do something with it...

# TODO: Exceptions are wildly inconsistent, some are critical, others can be skipped
#  Think about better structure

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()
    # bot.debug_apply_to_specific_job("https://www.linkedin.com/jobs/view/4020330291")
    time.sleep(4096)
