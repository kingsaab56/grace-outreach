import time


def countdown(seconds):

    while seconds > 0:

        print(f"Next email in {seconds} sec...", end="\r")

        time.sleep(1)

        seconds -= 1

    print("Ready to send.           ")