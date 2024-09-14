from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.INFO)

for name, logger in logging.root.manager.loggerDict.items():
    if name not in ["LinkedInClient", "LLMClient", "BrowserClient"]:
        logger.disabled = True

# TODO: This job breaks everything, but on the good side it has almost every element LinkedIn Easy Apply can contain
#  https://www.linkedin.com/jobs/view/4020330291
#  GOLIATH HAS FALLEN

# TODO: Add Canada work eligibility = false, true whatever
#  Add postal code = something, numbers
#  Add cover letter...
#  Add auto agree on terms and conditions = true, because the LLM rightfully doesn't know what to answer

# TODO: Rethink how error message is constructed

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()
    # bot.debug_apply_to_specific_job("https://www.linkedin.com/jobs/view/4020330291")
    time.sleep(4096)
