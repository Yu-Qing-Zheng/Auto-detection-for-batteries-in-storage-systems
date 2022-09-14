from sched import scheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from messager.dingtalk_chatbot import mychatrobot
from settings import seconds_interval
mychatrobot.energy_trigger_pusher()
scheduler = BlockingScheduler()
scheduler.add_job(mychatrobot.energy_trigger_pusher, 'interval', seconds = seconds_interval)
scheduler.start()