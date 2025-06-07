from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.INFO)

for name, logger in logging.root.manager.loggerDict.items():
    if name not in ["LinkedInClient", "LLMClient", "BrowserClient", "Delays", "CVManager"]:
        logger.disabled = True

# TODO: IT FAILS ON SINGLE PAGE APPLICATION FORMS

# TODO: Add Canada work eligibility = false, true whatever
#  Add postal code = something, numbers
#  Add cover letter...

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()
    # bot.debug_apply_to_specific_job("linkedin job link goes here <--")
    print("Went through every link, sleeping...")
    time.sleep(4096)
