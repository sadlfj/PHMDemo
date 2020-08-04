import datetime

from django.db import models

# Create your models here.
from gridfs import GridFS
from pymongo import MongoClient
from bson import ObjectId


class WaveInfo:

    # initial function for internal value
    def __init__(self):
        self.mongo_conn = MongoClient('localhost')
        self.mongo_db = self.mongo_conn['YANHU']
        self.wave_info_list = []

    # function for getting all the waves information
    def getAllWaveInfo(self):
        # get all wave files info
        coll_WaveFileInfo = self.mongo_db['WaveFileInfo']
        wave_file_info = (coll_WaveFileInfo.find({'id': {'$ne': '0'}, 'Label': {'$exists': False}},
                                                 {'RIFFID': 1,
                                                  'id': 1,  # it is the ObjectID of the file
                                                  'Device_name': 1,
                                                  'Time_stamp': 1,
                                                  'Label': 1,
                                                  'Channel1': 1,
                                                  'Channel2': 1,
                                                  'Channel3': 1,
                                                  'Channel4': 1,
                                                  'Channel5': 1,
                                                  '_id': 0,
                                                  }
                                                 )
                          )
        self.wave_info_list = []
        # get the total count of all channels
        for one in wave_file_info:
            one_total_channels = 0
            for x_one in range(1, 6):
                if ('Channel' + str(x_one)) in one.keys():
                    one_total_channels += 1
                    one.pop('Channel' + str(x_one))
            one['Total_channels'] = one_total_channels - 1
            self.wave_info_list.append(one)

        return self.wave_info_list.append

    # function for getting one wave information
    def getOneWaveInfo(self, time_stamp_filter: str):
        '''

        :param time_stamp_filter:
        :return:
        '''
        # get one file info
        coll_WaveFileInfo = self.mongo_db['WaveFileInfo']
        time_stamp = int(datetime.datetime.strptime(time_stamp_filter, '%Y-%m-%d %H:%M:%S').timestamp())
        wave_file_info = (coll_WaveFileInfo.find_one({'id': {'$ne': '0'}, 'Time_stamp': str(time_stamp)},
                                                     {'RIFFID': 1,
                                                      'id': 1,  # it is the ObjectID of the file
                                                      'Device_name': 1,
                                                      'Time_stamp': 1,
                                                      'Samples_per_second': 1,
                                                      'Channel1': 1,
                                                      # for one file we need to get the total channel's info
                                                      'Channel2': 1,
                                                      'Channel3': 1,
                                                      'Channel4': 1,
                                                      'Channel5': 1,
                                                      '_id': 0,
                                                      }
                                                     )
                          )
        # get the total count of all channels
        total_channels = 0
        for x in range(1, 6):
            if ('Channel' + str(x)) in wave_file_info.keys():
                total_channels += 1
        wave_file_info['Total_channels'] = total_channels

        return wave_file_info

    # functions for updating the label of one wave
    def updateOneWaveLabel(self, time_stamp_filter: str, device_name_filter: str, label: int):

        # get one file info
        coll_WaveFileInfo = self.mongo_db['WaveFileInfo']
        coll_WaveFileInfo.update_many({'Time_stamp': time_stamp_filter, 'Device_name': device_name_filter},
                                      {'$set': {'Label': label}}
                                      )
        print('Labelled it to ' + str(label))

    # functions for deleting the label of one wave
    def deleteOneWaveLabel(self):
        pass


class WaveFile:
    def __init__(self, wave_info: dict):
        '''

        :param wave_info:
        '''
        self.mongo_conn = MongoClient('localhost')
        self.mongo_db = self.mongo_conn['YANHU']
        self.wave_file_id = wave_info['id']

    def getWaveFile(self):
        # get fs
        fs = GridFS(self.mongo_db, 'wave_table')

        # get grid file
        return fs.get(fs.find_one({'_id': self.wave_file_id})._id)
