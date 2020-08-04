'''
# coding: utf-8
2020.06.26: 在鹏飞的版本上进行了完善，把所有字段都提取出来。
'''

import time
import wave
import numpy as np
import struct
from scipy.fftpack import fft, ifft
from scipy import signal, integrate
from scipy.signal import hilbert, welch, stft


class WaveExtractor:
    def __init__(self):
        pass

    def waveInfoExtract(self, filepath):
        '''
        contributed by DaiFu 打开WAV文件，提取属性数据
        :param filepath: 
        :return: 
        '''
        file = open(filepath, "rb")
        file_dict = {}
        channel_columns = ['name', 'unit', 'amplification', 'offset']
        file_dict['filepath'] = filepath

        # RIFF ID
        file.seek(0, 0)
        RIFFID_bytes = file.read(4).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())
        file_dict['RIFFID'] = RIFFID_bytes
        # RIFFID = ''.join([bin(ord(c)).replace('0b', '') for c in RIFFID_bytes])

        # Size in bytes
        file.seek(4, 0)
        Size_In_Bytes = file.read(4)
        SizeInBytes = int.from_bytes(Size_In_Bytes, byteorder='little', signed=False)
        file_dict['SizeInBytes'] = SizeInBytes

        # WAVE ID
        file.seek(8, 0)
        WAVE_ID_bytes = file.read(4).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())
        # WAVE_ID = ''.join([bin(ord(c)).replace('0b', '') for c in WAVE_ID_bytes])
        file_dict['WAVE_ID'] = WAVE_ID_bytes

        # Format chunk ID
        file.seek(12, 0)
        Format_chunk_ID_bytes = file.read(4).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())
        # Format_chunk_ID = ''.join([bin(ord(c)).replace('0b', '') for c in Format_chunk_ID_bytes])
        file_dict['Format_chunk_ID'] = Format_chunk_ID_bytes

        # Format tag
        file.seek(20, 0)
        Format_tag_bytes = file.read(2).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())
        file_dict['Format_tag'] = Format_tag_bytes

        # 通道数
        file.seek(22, 0)  # 表示从0开始，offset 22的位置开始读取数据
        Channels_number_bytes = file.read(2)  ##表示读取多少个字节
        Channels_number = int.from_bytes(Channels_number_bytes, byteorder='little', signed=False)  ##将二进制转换成数字
        print('Channels_number: ', Channels_number)
        file_dict['Channels_number'] = Channels_number

        # Samples per second
        file.seek(24, 0)  # 表示从0开始，offset 22的位置开始读取数据
        Samples_per_second_bytes = file.read(4)  ##表示读取多少个字节
        Samples_per_second = int.from_bytes(Samples_per_second_bytes, byteorder='little', signed=False)  ##将二进制转换成数字
        file_dict['Samples_per_second'] = Samples_per_second

        # Block alignment
        file.seek(32, 0)  # 表示从0开始，offset 22的位置开始读取数据
        Block_alignment_bytes = file.read(2)  ##表示读取多少个字节
        Block_alignment = int.from_bytes(Block_alignment_bytes, byteorder='little', signed=False)  ##将二进制转换成数字
        file_dict['Block_alignment'] = Block_alignment

        # CMS chunk ID
        file.seek(36, 0)  # 表示从0开始，offset 22的位置开始读取数据
        CMS_chunk_ID_bytes = file.read(4).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())  ##表示读取多少个字节
        # CMS_chunk_ID = ''.join([bin(ord(c)).replace('0b', '') for c in CMS_chunk_ID_bytes])
        file_dict['CMS_chunk_ID'] = CMS_chunk_ID_bytes

        # Device name
        file.seek(44, 0)  # 表示从0开始，offset 22的位置开始读取数据
        Device_name_bytes = file.read(256).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())  ##表示读取多少个字节
        # Device_name = bytes([int(x,2) for x in Device_name_bytes]).decode('utf-8')
        file_dict['Device_name'] = Device_name_bytes

        # 起始时间
        file.seek(300, 0)
        # pos=file.tell()
        Time_stamp_bytes = file.read(4)
        Time_stamp = int.from_bytes(Time_stamp_bytes, byteorder='little', signed=True)
        Time_array = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Time_stamp))
        file_dict['Time_stamp'] = str(Time_stamp)

        if Channels_number >= 1:
            # Channel name 1
            file.seek(308, 0)
            Channel1_name = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Unit name 1
            file.seek(372, 0)
            Channel1_unit = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Amplification系数 1
            file.seek(436, 0)
            Channel1_amplification_bytes = file.read(4)
            Channel1_amplification = struct.unpack('<f', Channel1_amplification_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            # 通道1 offset
            file.seek(440, 0)
            Channel1_offset_bytes = file.read(4)
            Channel1_offset = struct.unpack('<f', Channel1_offset_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            tmp_dict = dict(
                zip(channel_columns, [Channel1_name, Channel1_unit, Channel1_amplification, Channel1_offset]))
            file_dict['Channel1'] = tmp_dict

        if Channels_number >= 2:
            # Channel name 2
            file.seek(444, 0)
            Channel2_name = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Unit name 2
            file.seek(508, 0)
            Channel2_unit = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Amplification系数 2
            file.seek(572, 0)
            Channel2_amplification_bytes = file.read(4)
            Channel2_amplification = struct.unpack('<f', Channel2_amplification_bytes)[0]

            # 通道2 offset
            file.seek(576, 0)
            Channel2_offset_bytes = file.read(4)
            Channel2_offset = struct.unpack('<f', Channel2_offset_bytes)[0]

            tmp_dict = dict(
                zip(channel_columns, [Channel2_name, Channel2_unit, Channel2_amplification, Channel2_offset]))
            file_dict['Channel2'] = tmp_dict

        if Channels_number >= 3:
            # Channel name 3
            file.seek(580, 0)
            Channel3_name = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Unit name 3
            file.seek(644, 0)
            Channel3_unit = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Amplification系数 3
            file.seek(708, 0)
            Channel3_amplification_bytes = file.read(4)
            Channel3_amplification = struct.unpack('<f', Channel3_amplification_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            # 通道3 offset
            file.seek(712, 0)
            Channel3_offset_bytes = file.read(4)
            Channel3_offset = struct.unpack('<f', Channel3_offset_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            tmp_dict = dict(
                zip(channel_columns, [Channel3_name, Channel3_unit, Channel3_amplification, Channel3_offset]))
            file_dict['Channel3'] = tmp_dict

        if Channels_number >= 4:
            # Channel name 4
            file.seek(716, 0)
            Channel4_name = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Unit name 4
            file.seek(780, 0)
            Channel4_unit = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Amplification系数 4
            file.seek(844, 0)
            Channel4_amplification_bytes = file.read(4)
            Channel4_amplification = struct.unpack('<f', Channel4_amplification_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            # 通道4 offset
            file.seek(848, 0)
            Channel4_offset_bytes = file.read(4)
            Channel4_offset = struct.unpack('<f', Channel4_offset_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            tmp_dict = dict(
                zip(channel_columns, [Channel4_name, Channel4_unit, Channel4_amplification, Channel4_offset]))
            file_dict['Channel4'] = tmp_dict

        if Channels_number == 5:
            # Channel name 5
            file.seek(852, 0)
            Channel5_name = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())

            # Unit name 5
            file.seek(916, 0)
            Channel5_unit = file.read(64).decode('UTF-8', 'ignore').strip().strip(b'\x00'.decode())
            # Amplification系数 5
            file.seek(980, 0)
            Channel5_amplification_bytes = file.read(4)
            Channel5_amplification = struct.unpack('<f', Channel5_amplification_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            # 通道5 offset
            file.seek(984, 0)
            Channel5_offset_bytes = file.read(4)
            Channel5_offset = struct.unpack('<f', Channel5_offset_bytes)[0]  ##   ‘<f’：按照float浮点数来解析

            tmp_dict = dict(
                zip(channel_columns, [Channel5_name, Channel5_unit, Channel5_amplification, Channel5_offset]))
            file_dict['Channel5'] = tmp_dict

        else:
            Chnanel1_a = Chnanel2_a = Chnanel3_a = Chnanel4_a = Chnanel5_a = 0.0

        file.close()

        # print(Channel1_a, Channel2_a, Channel3_a)
        print("时间显示: ", Time_array)
        return file_dict

    def waveDataRead(self, path):
        '''
        contributed by DaiFu
        :param path:
        :return:
        '''
        f = wave.open(path, "rb")
        # 一次性返回所有的WAV文件的格式信息，它返回的是一个组元(tuple)：声道数, 量化位数（byte单位）,
        # 采样频率, 采样点数, 压缩类型, 压缩类型的描述。wave模块只支持非压缩的数据，因此可以忽略最后两个信息'''
        params = f.getparams()
        # 读取波形数据
        nchannels, sampwidth, framerate, nframes = params[:4]
        # 读取声音数据，传递一个参数指定需要读取的长度（以取样点为单位）
        str_date = f.readframes(nframes)
        f.close()
        # 需要根据声道数和量化单位，将读取的二进制数据转换为一个可以计算的数组
        wave_data = np.frombuffer(str_date, dtype=np.short)
        # 将wave_data数组改为通道数列，行数自动匹配。在修改shape的属性时，需使得数组的总长度不变。
        wave_data.shape = -1, nchannels
        # 转置数据,使成为通道数行行的数据，方便下面时间匹配
        wave_data = wave_data.T
        # 通过取样点数和取样频率计算出每个取样的时间,也就是周期T=采样单数/采样率；1秒钟取了46万个样本点
        x_time = np.around(np.arange(0, nframes) * (1.0 / framerate), decimals=2)
        return wave_data, list(map(float, x_time))

    def waveFFT(self, data: list, fs: int):
        '''
        contributed by XiePeng
        :param data:
        :param fs:
        :return:
        '''
        ...
        data = data - np.mean(data)
        nfft = len(data)
        amp = np.abs(fft(data, nfft)) / nfft
        freq = np.linspace(0, fs, nfft, False)
        if nfft % 2 == 0:
            amp[1:int(nfft / 2)] *= 2
            amp = amp[:int(nfft / 2) + 1]
            freq = np.around(freq[:int(nfft / 2) + 1], decimals=2)
        else:
            amp[1:int((nfft + 1) / 2)] *= 2
            amp = amp[:int((nfft + 1) / 2)]
            freq = np.around(freq[:int((nfft + 1) / 2)], decimals=2)
        return list(map(float, amp)), list(map(float, freq))

    def waveHilbertAmplitudeEnvelope(self, data: list):
        '''
        contributed by XiePeng
        :param data:
        :return:
        '''
        analytic_signal = hilbert(data)
        amplitude_envelop = np.abs(analytic_signal)
        return amplitude_envelop

    def doAccToVelocity(self, data: list, fs: int):
        '''
        Change Acc Singal into Velocity Signal -- Contributed by XiePeng
        :param data:
        :param fs:
        :return: list of Velocity Signal
        '''
        velocity = integrate.cumtrapz(data - np.mean(data), dx=1 / fs, initial=0)
        return list(velocity)

    def doEnvelope(self, data: list):
        '''
        Create the Envelope for Time-Domain or Frequency-Domain Signal -- Contributed by XiePeng
        :param data:
        :return: list of Envelope Signal
        '''
        analytic_signal = hilbert(data)
        amplitude_envelope = np.abs(analytic_signal)
        return list(amplitude_envelope)

    def doFFT(self, data: list, fs: int):
        '''
        Create Frequency-Domain Signal from the Time-Domain Signal -- Contributed by XiePeng
        :param data:
        :param fs:
        :return:
        '''
        nfft = len(data)
        amp = np.abs(fft(data, nfft)) / nfft
        freq = np.linspace(0, fs, nfft, False)
        if nfft % 2 == 0:
            amp[1:int(nfft / 2)] *= 2
            amp = amp[:int(nfft / 2) + 1]
            freq = freq[:int(nfft / 2) + 1]
        else:
            amp[1:int((nfft + 1) / 2)] *= 2
            amp = amp[:int((nfft + 1) / 2)]
            freq = freq[:int((nfft + 1) / 2)]
        return list(map(float, amp)), list(map(float, freq))

    def doSTFT(self, data: list, fs: int):
        re_freqs, re_time, re_Zxx = stft(data, fs)
        re_Zxx = re_Zxx.real
        result = []
        for foo_t in range(len(re_time)):
            # the ratio of compress to be defined, now it is 250
            if foo_t % 250 == 0:
                for foo_f in range(len(re_freqs)):
                    result.append([re_freqs[foo_f], re_time[foo_t], abs(re_Zxx[foo_f][foo_t])])
        return result, len(re_time), len(re_freqs)

    def doPowerSpectralDesnity(self, data: list, fs: int, window: str='hanning', noverlap=None):
        '''
        Create the Spectral of Power Desnity from the Time-Domain Signal -- Contributed by XiePeng
        :param data:
        :param fs:
        :param window:
        :param noverlap:
        :return:
        '''
        freq, psd = welch(data, fs, window=window, noverlap=noverlap)
        return list(psd), list(freq)





# wEx = waveExtractor()
# import os
# path = r"D:\FTPTEST"
# for filename in os.listdir(path):
#     print(os.path.join(path,filename))
#     dict1 = wEx.waveETLprocess(filepath=os.path.join(path, filename))
#     print(dict1)
#
#     wave_data, time = wEx.wave_read(r"D:\SiemensWork\ShiGang\sample_pengfei\20191011_014706______A_VIB1_VIB2.wav")
#     # average_fft(wave_data[0] * Channel1_a, 10240)
#     # # 左右声道的显示
#     # plt.figure()
#     # plt.subplot(311)
#     # plt.plot(time, wave_data[0] * Channel1_a)
#     # plt.title("VIB1")
#     # plt.subplot(312)
#     # plt.plot(time, wave_data[1] * Channel2_a)
#     # plt.title("VIB2")
#     # plt.subplot(313)
#     # plt.plot(time, wave_data[2] * Channel3_a)
#     # plt.title("Speed")
#     # plt.show()
#     # print('end')
# file = 'D:\\test\\20190525_073450______B_VIB1_VIB2.wav'
# waveETL = waveExtractor()
# file_info_dict = waveETL.waveInfoExtract(file)
# wave_data, time = waveETL.waveDataRead(file)
