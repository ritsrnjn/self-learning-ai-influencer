import schedule
import time

from data import posts_data
from manager import create_content_to_post

def run_scheduler():
    create_content_to_post()
    schedule.every(5).minutes.do(create_content_to_post)
    while True:
        schedule.run_pending()
        time.sleep(1)