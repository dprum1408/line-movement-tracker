import schedule
import time
from fetch_odds import fetch_odds

schedule.every(10).minutes.do(fetch_odds)

while True:
    schedule.run_pending()
    time.sleep(1)
