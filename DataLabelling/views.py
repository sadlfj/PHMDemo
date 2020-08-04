from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from DataLabelling.models import WaveInfo, WaveFile
from DataLabelling.WaveETLProcess import WaveExtractor
import json
import datetime


# Create your views here.
def main(request):
    # just a GET return the picture
    print('it is a ' + request.method + ' in function "main"')
    return render(request, 'data_labelling.html')
    if request.method == 'GET':
        # Step-1 get the file info
        waveInfo = WaveInfo()
        one_wave_info = waveInfo.getOneWaveInfo(TARGET_TIME)

        # Step-2 get one wave file
        waveFile = WaveFile(one_wave_info)
        wave_file = waveFile.getWaveFile()

        # Step-3 get time-series data from the wave file
        foo_waveExtractor = WaveExtractor()
        wave_timeY_list, time_points = foo_waveExtractor.waveDataRead(wave_file)

        fs = one_wave_info['Samples_per_second']

        # Step-4 initial data dict  {'time_points','speed_points',speed_unit','fs'}
        data = {
            'time_points': time_points,
            'speed_points': (wave_timeY_list[one_wave_info['Total_channels'] - 1] * (
                one_wave_info['Channel' + str(one_wave_info['Total_channels'])]['amplification'])).tolist(),
            'speed_unit': one_wave_info['Channel' + str(one_wave_info['Total_channels'])]['unit'],
            'fs': fs,
        }

        # Step-5 add the all channels result into channel_lists, so we have {'time_points','speed_points',speed_unit','fs','channel_lists'}
        channel_lists = []
        for foo in range(0, len(wave_timeY_list) - 1):
            channel_foo = {
                'channel_name': json.dumps(one_wave_info['Channel' + str(foo + 1)]['name']),
                'acc_points': (wave_timeY_list[0] * one_wave_info['Channel' + str(foo + 1)]['amplification']).tolist(),
                'vel_points': [],
                'acc_env_points': [],
                'vel_env_points': [],
                'freq_points': [],
                'acc_amp_points': [],
                'vel_amp_points': [],
                'psd_points': [],
                'psd_freq_points': [],
            }
            channel_foo['vel_points'] = foo_waveExtractor.doAccToVelocity(channel_foo['acc_points'], fs)
            channel_foo['acc_env_points'] = foo_waveExtractor.doEnvelope(channel_foo['acc_points'])
            channel_foo['vel_env_points'] = foo_waveExtractor.doEnvelope(channel_foo['vel_points'])
            channel_foo['acc_amp_points'], channel_foo['freq_points'] = foo_waveExtractor.doFFT(
                channel_foo['acc_points'], fs)
            channel_foo['vel_amp_points'] = foo_waveExtractor.doFFT(channel_foo['vel_points'], fs)[0]
            channel_foo['psd_points'], channel_foo['psd_freq_points'] = foo_waveExtractor.doPowerSpectralDesnity(
                channel_foo['acc_points'], fs)
            print('acc_points:', len(channel_foo['acc_points']))
            print('vel_points:', len(channel_foo['vel_points']))
            print('acc_env_points:', len(channel_foo['acc_env_points']))
            print('vel_env_points:', len(channel_foo['vel_env_points']))
            print('acc_amp_points:', len(channel_foo['acc_amp_points']))
            print('vel_amp_points:', len(channel_foo['vel_amp_points']))
            print('freq_points:', len(channel_foo['freq_points']))
            print('freq_points last:', channel_foo['freq_points'][len(channel_foo['freq_points']) - 1])
            print('psd_points:', len(channel_foo['psd_points']))
            print('psd_freq_points:', len(channel_foo['psd_freq_points']))
            print('psd_freq_points last:', channel_foo['psd_freq_points'][len(channel_foo['psd_freq_points']) - 1])
            print('~~~~~~~~~~~~~~~~~~~')
            channel_lists.append(channel_foo)
        data['channel_lists'] = channel_lists

        # Step-6 compress the data  To do ~~~~
        ratio_compress = 500
        data['time_points'] = data['time_points'][1::ratio_compress]
        data['speed_points'] = data['speed_points'][1::ratio_compress]
        for foo in range(len(data['channel_lists'])):
            for key in data['channel_lists'][foo].keys():
                if key != 'channel_name' and key != 'psd_points' and key != 'psd_freq_points':
                    data['channel_lists'][foo][key] = data['channel_lists'][foo][key][1::ratio_compress]

        for foo in range(len(data['channel_lists'])):
            for key in data['channel_lists'][foo].keys():
                print(len(data['channel_lists'][foo][key]))

        return JsonResponse(data)

        return render(request, 'data_labelling.html', context=data)

        # Step-5 add time series data into dict {'time_points','speed_points',speed_unit','fs','acc_points_list',}
        acc_points_list = []
        for foo in range(0, len(wave_timeY_list) - 1):
            acc_points_list.append(
                {
                    'channel_name': json.dumps(one_wave_info['Channel' + str(foo + 1)]['name']),
                    'data': (wave_timeY_list[foo] * one_wave_info['Channel' + str(foo + 1)]['amplification']).tolist(),
                    'value_name': 'acc_points_' + one_wave_info['Channel' + str(foo + 1)]['name'],
                }
            )
        data['acc_points_list'] = acc_points_list

        # Step-5 add time series data into dict {'time_points','speed_points',speed_unit','fs','acc_points_list','vel_points_list'}
        vel_points_list = []
        for foo in range(len(data['acc_points_list'])):
            vel_points_list.append(
                {
                    'channel_name': json.dumps(one_wave_info['Channel' + str(foo + 1)]['name']),
                    'data': foo_waveExtractor.doAccToVelocity(data['acc_points_list'][foo]['data'], fs),
                    'value_name': 'vel_points_' + one_wave_info['Channel' + str(foo + 1)]['name'],
                }
            )
        data['vel_points_list'] = vel_points_list

        return HttpResponse('done')

        # Step-6 get the frequency-series data into dict {'time_points','speed',speed_unit','acc_points_list','wave_freq','freq_channels_list','acc_unit'}
        freq_channels_list = []
        freq = one_wave_info['Samples_per_second']
        for foo in range(len(data['acc_points_list'])):
            freq_channels_list.append(
                {
                    'channel_name': json.dumps(one_wave_info['Channel' + str(foo + 1)]['name']),
                    'data': foo_waveExtractor.waveFFT(data['acc_points_list'][foo]['data'], freq)[0],
                    'value_name': 'freq_' + one_wave_info['Channel' + str(foo + 1)]['name'],
                }
            )
        data['wave_freq'] = foo_waveExtractor.waveFFT(data['acc_points_list'][0]['data'], freq)[1]
        data['freq_channels_list'] = freq_channels_list
        data['acc_unit'] = one_wave_info['Channel1']['unit']

        # compress the data to Json
        ratio_compress = 500
        data['time_points'] = data['time_points'][1::ratio_compress]
        data['speed'] = data['speed'][1::ratio_compress]
        data['wave_freq'] = data['wave_freq'][1::ratio_compress]
        for i in range(len(data['acc_points_list'])):
            data['acc_points_list'][i]['data'] = data['acc_points_list'][i]['data'][1::ratio_compress]
        for i in range(len(data['freq_channels_list'])):
            data['freq_channels_list'][i]['data'] = data['freq_channels_list'][i]['data'][1::ratio_compress]

        # string type must dumps to add ->""
        data['speed_unit'] = json.dumps(data['speed_unit'])
        data['acc_unit'] = json.dumps(data['acc_unit'])
        print(data)

        return render(request, 'data_labelling.html', context=data)
        # return JsonResponse(data)

    # Maybe we will have a POST


def wave_pic(request):
    print(request.POST)
    if request.method == 'POST':

        TARGET_TIME = request.POST.get('Time_stamp')
        TARGET_DEVICE = request.POST.get('Device_name')
        print(TARGET_TIME, TARGET_DEVICE)

        # Step-1 get the file info
        waveInfo = WaveInfo()
        one_wave_info = waveInfo.getOneWaveInfo(TARGET_TIME)

        # Step-2 get one wave file
        waveFile = WaveFile(one_wave_info)
        wave_file = waveFile.getWaveFile()

        # Step-3 get time-series data from the wave file
        foo_waveExtractor = WaveExtractor()
        wave_timeY_list, time_points = foo_waveExtractor.waveDataRead(wave_file)

        fs = one_wave_info['Samples_per_second']

        # Step-4 initial data dict  {'time_points','speed_points',speed_unit','fs'}
        data = {
            'device_name': one_wave_info['Device_name'],
            'time_stamp': one_wave_info['Time_stamp'],
            'time_points': time_points,
            'speed_points': (wave_timeY_list[one_wave_info['Total_channels'] - 1] * (
                one_wave_info['Channel' + str(one_wave_info['Total_channels'])]['amplification'])).tolist(),
            'speed_unit': one_wave_info['Channel' + str(one_wave_info['Total_channels'])]['unit'],
            'fs': fs,
        }

        # Step-5 add the all channels result into channel_list, so we have {'time_points','speed_points',speed_unit','fs','channel_list'}
        channel_list = []
        for foo in range(0, len(wave_timeY_list) - 1):
            channel_foo = {
                'channel_name': one_wave_info['Channel' + str(foo + 1)]['name'],
                'acc_points': (wave_timeY_list[0] * one_wave_info['Channel' + str(foo + 1)]['amplification']).tolist(),
                'vel_points': [],
                'acc_env_points': [],
                'vel_env_points': [],
                'freq_points': [],
                'acc_amp_points': [],
                'vel_amp_points': [],
                'psd_points': [],
                'psd_freq_points': [],
            }
            channel_foo['vel_points'] = foo_waveExtractor.doAccToVelocity(channel_foo['acc_points'], fs)
            channel_foo['acc_env_points'] = foo_waveExtractor.doEnvelope(channel_foo['acc_points'])
            channel_foo['vel_env_points'] = foo_waveExtractor.doEnvelope(channel_foo['vel_points'])
            channel_foo['acc_amp_points'], channel_foo['freq_points'] = foo_waveExtractor.doFFT(
                channel_foo['acc_points'], fs)
            channel_foo['vel_amp_points'] = foo_waveExtractor.doFFT(channel_foo['vel_points'], fs)[0]
            channel_foo['psd_points'], channel_foo['psd_freq_points'] = foo_waveExtractor.doPowerSpectralDesnity(
                channel_foo['acc_points'], fs)
            channel_foo['time-freq_points'], channel_foo['time-freq_intervalT'], channel_foo[
                'time-freq_intervalF'] = foo_waveExtractor.doSTFT(channel_foo['acc_points'], fs)
            print('acc_points:', len(channel_foo['acc_points']))
            print('vel_points:', len(channel_foo['vel_points']))
            print('acc_env_points:', len(channel_foo['acc_env_points']))
            print('vel_env_points:', len(channel_foo['vel_env_points']))
            print('acc_amp_points:', len(channel_foo['acc_amp_points']))
            print('vel_amp_points:', len(channel_foo['vel_amp_points']))
            print('freq_points:', len(channel_foo['freq_points']))
            print('freq_points last:', channel_foo['freq_points'][len(channel_foo['freq_points']) - 1])
            print('psd_points:', len(channel_foo['psd_points']))
            print('psd_freq_points:', len(channel_foo['psd_freq_points']))
            print('Time Freq Domain', len(channel_foo['time-freq_points']))
            print('~~~~~~~~~~~~~~~~~~~')
            channel_list.append(channel_foo)
        data['channel_list'] = channel_list

        # Step-6 compress the data  To do ~~~~
        ratio_compress = 500
        data['time_points'] = data['time_points'][1::ratio_compress]
        data['speed_points'] = data['speed_points'][1::ratio_compress]
        for foo in range(len(data['channel_list'])):
            for key in data['channel_list'][foo].keys():
                if key != 'channel_name' and key != 'psd_points' and key != 'psd_freq_points' and key != 'time-freq_points' and key != 'time-freq_intervalT' and key != 'time-freq_intervalF':
                    data['channel_list'][foo][key] = data['channel_list'][foo][key][1::ratio_compress]

        for foo in range(len(data['channel_list'])):
            for key in data['channel_list'][foo].keys():
                if key != 'time-freq_intervalT' and key != 'time-freq_intervalF':
                    print(len(data['channel_list'][foo][key]))

        return JsonResponse(data)


def wave_table(request):
    # request' body
    print('it is a ' + request.method + ' in function "wave_table"')
    index_start = int(request.GET.get('offset'))
    index_end = int(request.GET.get('limit')) + index_start
    print(index_start, index_end)

    if request.method == 'GET':
        # get file info
        waveInfo = WaveInfo()
        waveInfo.getAllWaveInfo()
        wave_info_list = waveInfo.wave_info_list

        # pop no-useful keys and change Time_stamp's format
        for x in wave_info_list:
            x.pop('id')
            x['Time_stamp'] = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(int(x['Time_stamp'])), '%Y-%m-%d %H:%M:%S'
            )

        # get the data as pagination format
        pagination_rows = {
            'total': len(wave_info_list),
            'rows': wave_info_list[index_start: index_end],
        }

        # we need to use safe=False to serialize the non-dict value
        return JsonResponse(pagination_rows)

    elif request.method == 'POST':
        # get file info
        waveInfo = WaveInfo()
        waveInfo.getAllWaveInfo()
        wave_info_list = waveInfo.wave_info_list
        for x in wave_info_list:
            x.pop('id')
            x['Time_stamp'] = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(int(x['Time_stamp'])), '%Y-%m-%d %H:%M:%S'
            )
        result = {
            'total': len(wave_info_list),
            'rows': wave_info_list[index_start: index_end],
        }

        # we need to use safe=False to serialize the non-dict value
        return JsonResponse(result, safe=False)


def wave_label(request):
    if request.method == 'GET':
        print('it is a ' + request.method + ' in function "wave_label"')
        print(request.GET)
    elif request.method == 'POST':
        print('it is a ' + request.method + ' in function "wave_label"')
        TARGET_TIME = request.POST.get('Time_stamp')
        TARGET_DEVICE = request.POST.get('Device_name')
        LABEL = request.POST.get('Label')
        print(TARGET_TIME, TARGET_DEVICE)

        # Step-1 get the update the file label
        waveInfo = WaveInfo()
        waveInfo.updateOneWaveLabel(TARGET_TIME, TARGET_DEVICE, int(LABEL))

        data = {'result': 'success'}
        return JsonResponse(data)
