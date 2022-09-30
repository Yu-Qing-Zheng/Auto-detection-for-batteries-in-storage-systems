"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

import argparse
import json
import time
import numpy as np

from soc.exp.exp_informer import Exp_Informer

from soc.main.db.db_connect import rdc
from soc.utils import logger
from soc.config import base_config


class SOC:
    def __init__(self, plc_id, data_time, abnormal_voltage, abnormal_current, abnormal_temperature, abnormal_status):
        self.rdc = rdc
        self.plc_id = plc_id
        self.data_time = data_time
        
        self.soc_depend_info = None
        self.abnormal_voltage = abnormal_voltage
        self.abnormal_current = abnormal_current
        self.abnormal_temperature = abnormal_temperature
        self.abnormal_status = abnormal_status
        self.data = self._select_data()

    # 取 datalog 最新一条数据进行格式化
    def _select_data(self):
        tmp_data = dict()

        for a in range(1, 11):
            for b in range(1, 25):
                tmp_data[f"{a}组{b}号电池电压"] = self.abnormal_voltage

        tmp_data["PLC_id"] = self.plc_id

        tmp_data["PCS电池电流"] = self.abnormal_current

        for c in range(1, 11):
            for d in range(1, 3):
                tmp_data[f"{c}组电池温度{d}"] = self.abnormal_temperature

        return tmp_data

    def _get_soc_depend_info(self, current):
        context_soc = -1.0

        contextDelta = 0.001
        if abs(current) > 100:
            contextDelta = abs(current) / 16000
        elif abs(current) > 75:
            contextDelta = 0.007
        elif abs(current) > 60:
            contextDelta = 0.005
        elif abs(current) > 30:
            contextDelta = 0.003

        soc_depend_info_str = self.rdc.get(f"{base_config.DEPEND_INFO_PREFIX}{self.plc_id}")
        if not soc_depend_info_str or soc_depend_info_str == "null":
            self.soc_depend_info = {
                "status": -1,
                "predict_soc": -1.0,
                "context_soc": -1.0,
            }
        else:
            self.soc_depend_info = json.loads(soc_depend_info_str)
        self.soc_depend_info["status"] = self.abnormal_status

        # 首次启用 context_soc 仅从 0 & 1.0 校准时刻开始
        if self.soc_depend_info["status"] == 0:
            context_soc = 0.0
        elif self.soc_depend_info["status"] == 1:
            context_soc = 1.0
        else:
            if self.soc_depend_info["context_soc"] != -1.0:
                context_soc = self.soc_depend_info["context_soc"]
                if current > 0:
                    context_soc -= contextDelta
                elif current < 0:
                    context_soc += contextDelta

                if context_soc > 0.999:
                    context_soc = 0.999
                elif context_soc < 0.001:
                    context_soc = 0.001
        self.data["context_soc"] = context_soc
        self.soc_depend_info["context_soc"] = context_soc

    def _get_predict_soc(self):
        print('!!!!')
        parser = argparse.ArgumentParser(description='Informer')
        parser.add_argument('--cols', type=str, nargs='+', help='certain cols from the data files as the input features')
        args = parser.parse_args(args=[])
        args.e_layers = 2
        args.enc_in = 4
        args.dec_in = 4
        args.c_out = 1
        args.seq_len = 5
        args.label_len = 4
        args.pred_len = 1
        args.factor = 5
        args.d_model = 512
        args.n_heads = 8
        args.d_layers = 1
        args.d_ff = 2048
        args.dropout = 0.05
        args.attn = 'prob'
        args.embed = 'timeF'
        args.freq = 't'
        args.activation = 'gelu'
        args.output_attention = False
        args.distil = True
        args.mix = True
        args.use_multi_gpu = False
        args.data = 'SOC'
        args.detail_freq = 't'
        args.root_path = './data/'
        args.data_path = 'SOC.csv'
        args.features = 'MS'

        args.target = 'SOC'
        args.inverse = False
        args.batch_size = 32
        args.num_workers = 0
        args.padding = 0
        args.use_amp = False
        Exp = Exp_Informer
        exp = Exp(args)
        aaa = (exp.predict(self.plc_id))[0][0][0][3]
        print(aaa)
        return aaa

    def _get_predict_monotonous(self, current, predict_soc):
        # predict 单调
        soc_depend_info_str = self.rdc.get(f"{base_config.DEPEND_INFO_PREFIX}{self.plc_id}")
        if soc_depend_info_str:
            soc_depend_info = json.loads(soc_depend_info_str)
            delta = 0.001
            if current != 0 and predict_soc < 0.1:
                delta = 0.01
            if not np.isnan(predict_soc):
                logger.info("not np.isnan")
                if soc_depend_info["status"] == -1 or soc_depend_info["status"] == -99:
                    # 放电
                    if current > 0:
                        if predict_soc >= soc_depend_info["predict_soc"]:
                            # 1. 预测的浮动导致的反单调方向数值
                            # 2. delta 累计导致的预测数值一直处在反单调方向上而被拒绝
                            # 所以仅保持
                            predict_soc = soc_depend_info["predict_soc"]
                        else:
                            # predictSOC 提前 == 0
                            if predict_soc <= 0:
                                predict_soc = soc_depend_info["predict_soc"]
                                predict_soc -= delta
                    # 充电
                    elif current < 0:
                        if predict_soc <= soc_depend_info["predict_soc"]:
                            # 1. 预测的浮动导致的反单调方向数值
                            # 2. delta 累计导致的预测数值一直处在反单调方向上而被拒绝
                            # 所以仅保持
                            predict_soc = soc_depend_info["predict_soc"]
                        else:
                            # predictSOC 提前 == 1
                            if predict_soc >= 1.0:
                                predict_soc = soc_depend_info["predict_soc"]
                                predict_soc += delta
                    # 静置
                    elif current == 0:
                        predict_soc = soc_depend_info["predict_soc"]

            # predictSOC 为 NaN
            else:
                logger.info("np.isnan")
                predict_soc = soc_depend_info["predict_soc"]
                if predict_soc > 0.9:
                    if abs(current) > 100:
                        delta = 0.009
                    elif abs(current) > 75:
                        delta = 0.007
                    elif abs(current) > 60:
                        delta = 0.005
                    elif abs(current) > 30:
                        delta = 0.003

                if current > 0:
                    predict_soc -= delta
                elif current < 0:
                    predict_soc += delta

            # status == -1 or -999
            if soc_depend_info["status"] != 0 and soc_depend_info["status"] != 1:
                if predict_soc > 0.999:
                    predict_soc = 0.999
                elif predict_soc < 0.001:
                    predict_soc = 0.001
            # status == 0 or 1
            elif current != 0:
                predict_soc = soc_depend_info["predict_soc"]
                if soc_depend_info["status"] == 0:
                    predict_soc -= delta
                else:
                    predict_soc += delta
                if predict_soc > 0.999:
                    predict_soc = 0.999
                elif predict_soc < 0.001:
                    predict_soc = 0.001
        return predict_soc

    @property
    def predict_soc(self):
        predict_soc = -1.0

        current = self.data['PCS电池电流']

        # Redis: 准备供预测的 5 个点
        plcList = self.rdc.lrange(self.plc_id, 0, -1)
        self._get_soc_depend_info(current)

        # Redis 数据量 >= 5 之后既丢又存
        if plcList:
            if len(plcList) >= 9:
                self.rdc.lpop(self.plc_id)
                if not self.soc_depend_info["status"] and not current:
                    predict_soc = 0.0
                elif self.soc_depend_info["status"] == 1 and not current:
                    predict_soc = 1.0
                else:
                    logger.info("get predict soc")
                    predict_soc = self._get_predict_soc()
            logger.info(predict_soc)
            predict_soc = self._get_predict_monotonous(current, predict_soc)
        self.soc_depend_info["predict_soc"] = float(predict_soc)

        # 每运行一次都会存
        self.rdc.rpush(self.plc_id, json.dumps({
            'time': self.data_time,
            'context_soc': self.soc_depend_info["context_soc"],
            'data': self.data
        }))

        return predict_soc

    def __del__(self):
        self.rdc.set(f"{base_config.DEPEND_INFO_PREFIX}{self.plc_id}", json.dumps(self.soc_depend_info))


# 输入的第一条数据需要是开始充放电前 静置段的最后一条数据
# abnormal_time 为 datalog time
# abnormal_status 为 0/1 or -1
# time.time() 为时间戳作为 plc id
# soc = SOC(time.time(), abnormal_time, abnormal_voltage, abnormal_current, abnormal_temperature, abnormal_status)
# print(soc.predict_soc)
