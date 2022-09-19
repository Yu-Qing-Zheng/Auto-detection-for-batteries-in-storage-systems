from sched import scheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from energy.trigger_loop import trigger_loop
# from settings import seconds_interval
import importlib

settings = importlib.import_module('settings')
# importlib.reload(settings)
trigger_loop()
scheduler = BlockingScheduler()
scheduler.add_job(trigger_loop, 'interval', seconds = settings.seconds_interval)
scheduler.start()

# def main():
#     pass

# if __name__ == "__main__":
#     pass