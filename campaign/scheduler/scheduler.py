from campaign.scheduler.queue import CampaignQueue
from campaign.scheduler.timer import countdown


class CampaignScheduler:

    def __init__(self):

        self.queue = CampaignQueue()

        self.delay = 5

        self.sent = 0


    def load_contacts(self, emails):

        for email in emails:
            self.queue.add(email)


    def start(self):

        print("\n========== CAMPAIGN STARTED ==========\n")

        while self.queue.count() > 0:

            email = self.queue.get_next()

            print(f"Preparing: {email}")

            countdown(self.delay)

            print(f"Draft Ready -> {email}\n")

            self.sent += 1


        print("\nCampaign Finished.")
        print(f"Total Processed : {self.sent}")