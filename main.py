from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.DEBUG)

for name, logger in logging.root.manager.loggerDict.items():
    if name not in ["LinkedInClient", "LLMClient", "BrowserClient", "Delays"]:
        logger.disabled = True

# TODO: Add Canada work eligibility = false, true whatever
#  Add postal code = something, numbers
#  Add cover letter...

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()
    # I think this form has everything linkedin can throw at me
    # https://www.linkedin.com/jobs/search/?currentJobId=4242868836&f_AL=true&f_E=2%2C3%2C4&f_I=109&f_JT=F&f_TPR=r604800&f_WT=1%2C2%2C3&keywords=Gameplay%20Developer&location=Canada&origin=JOB_SEARCH_PAGE_OTHER_ENTRY
    # bot.debug_apply_to_specific_job("https://www.linkedin.com/jobs/view/principal-generalist-engineer-ue4-5-at-steel-city-interactive-4231854311/?originalSubdomain=uk")
    print("Went through every link, sleeping...")
    time.sleep(4096)
