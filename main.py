from linkedin_client import LinkedInClient
import time
import logging

logging.basicConfig(level=logging.INFO)

for name, logger in logging.root.manager.loggerDict.items():
    if name not in ["LinkedInClient", "LLMClient", "BrowserClient"]:
        logger.disabled = True

# TODO: This job breaks everything, but on the good side it has almost every element LinkedIn Easy Apply can contain
#  https://www.linkedin.com/jobs/view/4020330291/?alternateChannel=search&refId=XBib2p2jqdpPHpBY0CkNng%3D%3D&trackingId=izNHfeU8gbBXgsfRv7V3Zw%3D%3D&trk=d_flagship3_search_srp_jobs

# TODO: Add Canada work eligibility
#  Add postal code
#  Add cover letter...

if __name__ == '__main__':
    bot = LinkedInClient()
    bot.start()
    time.sleep(4096)
