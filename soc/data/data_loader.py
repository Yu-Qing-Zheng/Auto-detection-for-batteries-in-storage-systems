"""
# @Author: ZeKai
# @Date: 2022-03-07
"""
import json

import numpy as np
import pandas as pd

from torch.utils.data import Dataset

from soc.main.db.db_connect import rdc
from soc.utils.tools import StandardScaler
from soc.utils.timefeatures import time_features

import warnings

warnings.filterwarnings('ignore')


# 取中值
def get_median(data):
    size = len(data)

    data = sorted(data)
    if size % 2 == 0:
        median = (data[size // 2] + data[size // 2 - 1]) / 2
        data[0] = median
    if size % 2 == 1:
        median = data[(size - 1) // 2]
        data[0] = median
    return data[0]


class Dataset_Pred(Dataset):
    def __init__(self, plc, root_path, flag='pred', size=None,
                 features='MS', data_path='SOC.csv',
                 target='SOC', scale=True, inverse=False, timeenc=0, freq='t', cols=None):
        if size is None:
            self.seq_len = 24 * 4 * 4
            self.label_len = 24 * 4
            self.pred_len = 24 * 4
        else:
            self.seq_len = size[0]
            self.label_len = size[1]
            self.pred_len = size[2]
        assert flag in ['pred']

        self.rdc = rdc
        self.plc = plc
        self.features = features
        self.target = target
        self.scale = scale
        self.inverse = inverse
        self.timeenc = timeenc
        self.freq = freq
        self.cols = cols
        self.root_path = root_path
        self.data_path = data_path
        self.__read_data__()

    def __read_data__(self):
        self.scaler = StandardScaler()

        plcList = self.rdc.lrange(self.plc, 0, -1)
        num = len(plcList)
        date = []
        data = []
        soc = []
        for i in range(num-5, num):
            redis_data = json.loads(plcList[i])
            date.append(redis_data['time'])
            soc.append(redis_data['context_soc'])
            data.append(redis_data['data'])

        # 预测 list
        voltage = []
        current = []
        temperature = []

        # 取 Redis 数据库中最新 5 条供预测的数据
        for i in range(0, 5):
            # 取中值 list
            vol = []
            temp = []

            # ab 循环取的是一条数据中的 10 * 24 个电压数据
            for a in range(1, 11):
                for b in range(1, 25):
                    vol.append(data[i][str(a) + '组' + str(b) + '号电池电压'])
            voltage.append(get_median(vol))

            current.append(data[i]['PCS电池电流'])

            # cd 循环取的是 10 * 2 个温度数据
            for c in range(1, 11):
                for d in range(1, 3):
                    temp.append(data[i][str(c) + '组电池温度' + str(d)])
            temperature.append(get_median(temp))

        df_raw = pd.DataFrame(
            {
                "date": date,
                "Voltage": voltage,
                "Current": current,
                "Temperature": temperature,
                "SOC": soc,
            }
        )
        for i in range(0, 5):
            print((df_raw.values.tolist())[i])

        if self.cols:
            cols = self.cols.copy()
            cols.remove(self.target)
        else:
            cols = list(df_raw.columns)
            cols.remove(self.target)
            cols.remove('date')
        df_raw = df_raw[['date'] + cols + [self.target]]

        border1 = len(df_raw) - self.seq_len
        border2 = len(df_raw)

        if self.features == 'M' or self.features == 'MS':
            cols_data = df_raw.columns[1:]
            df_data = df_raw[cols_data]
        elif self.features == 'S':
            df_data = df_raw[[self.target]]

        if self.scale:
            self.scaler.fit(df_data.values)
            data = self.scaler.transform(df_data.values)
        else:
            data = df_data.values

        tmp_stamp = df_raw[['date']][border1:border2]
        tmp_stamp['date'] = pd.to_datetime(tmp_stamp.date)
        pred_dates = pd.date_range(tmp_stamp.date.values[-1], periods=self.pred_len + 1, freq=self.freq)

        df_stamp = pd.DataFrame(columns=['date'])
        df_stamp.date = list(tmp_stamp.date.values) + list(pred_dates[1:])
        data_stamp = time_features(df_stamp, timeenc=self.timeenc, freq=self.freq[-1:])

        self.data_x = data[border1:border2]
        if self.inverse:
            self.data_y = df_data.values[border1:border2]
        else:
            self.data_y = data[border1:border2]
        self.data_stamp = data_stamp

    def __getitem__(self, index):
        s_begin = index
        s_end = s_begin + self.seq_len
        r_begin = s_end - self.label_len
        r_end = r_begin + self.label_len + self.pred_len

        seq_x = self.data_x[s_begin:s_end]
        if self.inverse:
            seq_y = self.data_x[r_begin:r_begin + self.label_len]
        else:
            seq_y = self.data_y[r_begin:r_begin + self.label_len]
        seq_x_mark = self.data_stamp[s_begin:s_end]
        seq_y_mark = self.data_stamp[r_begin:r_end]

        return seq_x, seq_y, seq_x_mark, seq_y_mark

    def __len__(self):
        return len(self.data_x) - self.seq_len + 1

    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data)
