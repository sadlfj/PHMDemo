from bson import ObjectId
from pymongo import MongoClient
from gridfs import GridFS
from DataLabelling import WaveETLProcess


# get db
mongo_conn = MongoClient('localhost')
db_YANHU = mongo_conn['YANHU']

# get file info
collection_WaveFileInfo = db_YANHU['WaveFileInfo']
wave_file_info = (collection_WaveFileInfo.find_one({'id': ObjectId("5efb48e229ef50f9239f09d9")},
                                                   {'_id': 0}
                                                   ))
for key in wave_file_info:
    print(key, ':', wave_file_info[key])
wave_file_id = wave_file_info['id']
print('the file ID is : ' + str(wave_file_id))

# get fs
fs = GridFS(db_YANHU, 'wave_table')

# get grid file
wave_file = fs.get(fs.find_one({'_id': wave_file_id})._id)

# get the time_series data in wave file
foo_waveExtractor = WaveETLProcess.WaveExtractor()
wave_data_list, wave_time = foo_waveExtractor.waveDataRead(wave_file)
for wave_data in wave_data_list:
    print(len(wave_data[0::100]))
    # foo_waveExtractor.waveAverageFFT(wave_data, 100)
print(len(wave_time))
print(min(wave_time), max(wave_time))
print(len(wave_data_list[0]))

