from re import S
from dingtalkchatbot.chatbot import DingtalkChatbot
from energy.maximum_energy_calculate import maximum_energy_calculate
from mongodb.query_request import query_request
from clock.get_current_time import get_current_time
import datetime
import pandas as pd
from settings import energy_trigger_sender_webhook, plc_csv_file, plc_csv_path, energy_trigger_sender_secret, \
    bot_query_dayrange, filter_for_energy_trigger, filter_for_energy_threshold, fmt1

class mychatrobot:

    @staticmethod
    def energy_trigger_sender(message):
        webhook = energy_trigger_sender_webhook
        secret = energy_trigger_sender_secret
        bot = DingtalkChatbot(webhook, secret=secret)
        bot.send_text(msg=message, is_at_all=False)

    @staticmethod
    def get_trigger(plc):
        now_time = get_current_time()[0]
        now_time_ts = datetime.datetime.strptime(now_time, fmt1)
        start_time_ts = now_time_ts - datetime.timedelta(days=bot_query_dayrange)
        data = query_request.trigger_query(start_time_ts, now_time_ts, plc, \
            filter_for_energy_trigger)
        if len(data) > 0:
            energy_flag = data[0]['energy_flag']
            return energy_flag

    @staticmethod
    def get_thresold(plc):
        forward_threshold = -1
        reverse_threshold = -1
        now_time = get_current_time()[0]
        now_time_ts = datetime.datetime.strptime(now_time, fmt1)
        df_plc_list = pd.read_csv(plc_csv_path+plc_csv_file)
        start_time = str(df_plc_list[df_plc_list['plc']==plc[0]]['time'].values[0])
        start_time_ts = datetime.datetime.strptime(start_time, fmt1)
        data = query_request.threshold_query(start_time_ts, now_time_ts, plc, \
            filter_for_energy_threshold)
        if len(data) > 0:
            forward_threshold = data[0]['median_max_forward']
            reverse_threshold = data[0]['median_max_reverse']
        
        return [forward_threshold, reverse_threshold]

    @staticmethod
    def get_max(plc):
        max_f = -1
        max_r = -1
        max_energy = maximum_energy_calculate(plc)
        if len(max_energy) > 0:
            max_f = max_energy[0]
            max_r = max_energy[1]
        return [max_f, max_r]
    
    @staticmethod
    def energy_trigger_pusher():
        df_plc = pd.read_csv(plc_csv_path+plc_csv_file)
        plcset = df_plc['plc'].values
        minus_set = []
        zero_set = []
        one_set = []
        for i in range(0, len(plcset)):
            plc = [int(plcset[i])]
            energy_flag = mychatrobot.get_trigger(plc)
            if energy_flag == 0:
                zero_set.append(plc[0])
            if energy_flag == -1:
                minus_set.append(plc[0])
            if energy_flag == 1:
                one_set.append(plc[0])
        text_to_alert = ''
        # one_set = plcset
        if len(one_set) > 0:
            for i in range(0, len(one_set)):
                plc = [int(one_set[i])]
                threshold = mychatrobot.get_thresold(plc)
                max = mychatrobot.get_max(plc)
                text_report = 'PLC_id:'+str(plc[0])+', \n'+\
                            '[单次充电量标准]forward:'+str(threshold[0])+', \n[单次放电量标准]reverse:'+str(threshold[1])+', \n'+\
                            '[24小时内最大单次充电量]forward:'+str(max[0])+', \n[24小时内最大单次放电量]reverse:'+str(max[1])+', \n充放电量低于预期。\n######\n'
                text_to_alert += text_report
        mychatrobot.energy_trigger_sender(text_to_alert)
