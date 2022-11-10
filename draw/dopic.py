from mysql.mysql_model import *
import importlib
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter

class dopic:
    @staticmethod
    def checkfile():
        # try:
        settings = importlib.import_module('settings')
        if os.path.exists(settings.figpath):
            shutil.rmtree(settings.figpath)
            os.mkdir(settings.figpath)
        else:
            os.mkdir(settings.figpath)
        # except:
        #     print('error on checkfile.')

    @staticmethod
    def dsox():
        # try:
        settings = importlib.import_module('settings')
        mysql_session = get_session()
        data_query = mysql_session.query(diff_sox).all()
        mysql_session.close()
        if len(data_query) == 0:
            pass
        else:
            df_data = pd.DataFrame()
            for i in range(0, len(data_query)):
                data_series = {'time': data_query[i].time}
                data_series.update({'plc_id': data_query[i].plc_id})
                data_series.update({'bat_id': data_query[i].bat_id})
                data_series.update({'voltage': data_query[i].voltage})
                data_series.update({'soc': data_query[i].soc})
                data_series.update({'soc_bound': data_query[i].soc_bound})
                data_series.update({'soh': data_query[i].soh})
                data_series.update({'soh_bound': data_query[i].soh_bound})
                data_series.update({'voltage_bench': data_query[i].voltage_bench})
                data_series.update({'soc_bench': data_query[i].soc_bench})
                data_series.update({'soc_bound_bench': data_query[i].soc_bound_bench})
                data_series.update({'soh_bench': data_query[i].soh_bench})
                data_series.update({'soh_bound_bench': data_query[i].soh_bound_bench})
                data_series.update({'diff_soc': data_query[i].diff_soc})
                data_series.update({'diff_soc_bound': data_query[i].diff_soc_bound})
                data_series.update({'diff_soh': data_query[i].diff_soh})
                data_series.update({'diff_soh_bound': data_query[i].diff_soh_bound})
                to_append_to_data = pd.DataFrame(data_series, index=[0])
                df_data = pd.concat([df_data, to_append_to_data], axis=0)
            df_data = df_data.sort_values(by='time', ascending=True)
            df_data = df_data.reset_index(drop=True)
            plc_set = df_data['plc_id'].unique()
            for plc in plc_set:
                df_1p = df_data[df_data['plc_id'].isin([plc])]
                bat_set = df_1p['bat_id'].unique()
                for thebat in bat_set:
                    if 'median' in thebat:
                        pass
                    else:
                        # print('bat_id:', thebat)
                        df_1p_1b = df_1p[df_1p['bat_id'].isin([thebat])]
                        figname = str(plc)+'_'+thebat+'.png'
                        fig, (ax_v, ax_z, ax_h) = plt.subplots(3, 1, dpi=600, sharex=True)
                        x_t = df_1p_1b['time'].values
                        y_v = df_1p_1b['voltage'].values
                        y_v_b = df_1p_1b['voltage_bench'].values
                        y_dz = df_1p_1b['diff_soc'].values
                        y_dh = df_1p_1b['diff_soh'].values
                        ax_v.plot(x_t, y_v, label=str(plc)+'_'+thebat)
                        ax_v.plot(x_t, y_v_b, label='benchmark')
                        ax_v.set_ylabel('Voltage (V)')
                        # ax_v.set_title('Voltage-Time', fontsize=settings.fontsize)
                        ax_v.legend()
                        ax_v.grid(True)
                        ax_v.grid(color = 'k', ls = '-.', lw = 0.5)
                        ax_z.plot(x_t, y_dz, label='dSOC')
                        ax_z.set_ylabel('dSOC')
                        # ax_z.set_title('Difference of SOC', fontsize=settings.fontsize)
                        ax_z.legend()
                        ax_z.grid(True)
                        ax_z.grid(color = 'k', ls = '-.', lw = 0.5)
                        ax_h.plot(x_t, y_dh, label='dSOH')
                        locator = AutoDateLocator(minticks=4, maxticks=10)
                        ax_h.xaxis.set_major_locator(locator)
                        ax_h.xaxis.set_major_formatter(ConciseDateFormatter(locator))
                        # ax_h.set_title('Difference of SOH', fontsize=settings.fontsize)
                        ax_h.set_xlabel('Time')
                        ax_h.set_ylabel('dSOH')
                        ax_h.legend()
                        ax_h.grid(color = 'k', ls = '-.', lw = 0.5)
                        plt.savefig(settings.figpath+figname)

        # except:
        #     print('error on dsox.')

    @staticmethod
    def packpic():
        # try:
        settings = importlib.import_module('settings')
        mysql_session = get_session()
        data_query = mysql_session.query(sox_calculation).all()
        mysql_session.close()
        if len(data_query) == 0:
            pass
        else:
            df_data = pd.DataFrame()
            for i in range(0, len(data_query)):
                data_series = {'time': data_query[i].time}
                data_series.update({'plc_id': data_query[i].plc_id})
                data_series.update({'bat_id': data_query[i].bat_id})
                data_series.update({'voltage': data_query[i].voltage})
                data_series.update({'soc': data_query[i].soc})
                data_series.update({'soc_bound': data_query[i].soc_bound})
                data_series.update({'soh': data_query[i].soh})
                data_series.update({'soh_bound': data_query[i].soh_bound})
                to_append_to_data = pd.DataFrame(data_series, index=[0])
                df_data = pd.concat([df_data, to_append_to_data], axis=0)
            df_data = df_data.sort_values(by='time', ascending=True)
            df_data = df_data.reset_index(drop=True)
            plc_set = df_data['plc_id'].unique()
            for plc in plc_set:
                df_1p = df_data[df_data['plc_id'].isin([plc])]
                fig, (ax_v, ax_z) = plt.subplots(2, 1, dpi=600)
                figname = str(plc) + '_packs.png'
                for i in range(1, settings.pack_num+1):
                    thebat = 'median_' + str(i)
                    df_1p_median = df_1p[df_1p['bat_id'].isin([thebat])]
                    df_1p_median = df_1p_median.sort_values(by='time', ascending=True)
                    x_t = df_1p_median['time'].values
                    y_v = df_1p_median['voltage'].values
                    y_z = df_1p_median['soc'].values
                    ax_v.plot(x_t, y_v, label = 'Pack ' + str(i))
                    ax_z.plot(x_t, y_z, label = 'Pack ' + str(i))
                ax_v.set_xlabel('Time')
                ax_v.set_ylabel('Voltage')
                ax_v.grid(True)
                # ax_v.legend()
                ax_v.grid(color = 'k', ls = '-.', lw = 1)
                ax_z.set_xlabel('Time')
                ax_z.set_ylabel('SOC')
                ax_z.grid(True)
                # ax_z.legend()
                ax_z.grid(color = 'k', ls = '-.', lw = 1)
                locator = AutoDateLocator(minticks=4, maxticks=10)
                ax_z.xaxis.set_major_locator(locator)
                ax_z.xaxis.set_major_formatter(ConciseDateFormatter(locator))
                plt.savefig(settings.figpath+figname)
        # except:
        #     print('error on packpic.')
