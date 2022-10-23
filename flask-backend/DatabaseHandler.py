import array
import json
import string

from flask_pymongo import MongoClient

import constants


def preprocess_data_string(data: string):
    data = data.replace(':false,', ':False,').replace(':true,', ':True,')
    data = data.split('\n')

    data_points = []
    for data_point_string in data:
        try:
            data_point = eval(data_point_string)
            data_points.append(data_point)
        except Exception as e:
            print(e)
    return data_points


def filter_data_points_for_collection(collection_name: string, data_points: array):
    result = []
    for data_point in data_points:
        if data_point['name'] == collection_name:
            result.append(data_point)
    return result


class DatabaseHandler:

    def __init__(self, mongo_uri):
        self.mongo = MongoClient(mongo_uri)  # here mongo_client; but parameter is string to mongodb server

    def write_nmaprun_to_database(self, nmap_report_json: string):
        try:
            nmap_report = json.loads(nmap_report_json)
            self.insert_one_into(constants.COLLECTION_NAME_NMAPRUN, nmap_report)
        except Exception as e:
            print(e)
            return

    def write_all_to_database(self, collection_name: string, data: string):
        data_points = preprocess_data_string(data)
        data_points = filter_data_points_for_collection(collection_name, data_points)

        if len(data_points) > 0:
            result = self.insert_many_into(collection_name, data_points)
            print(str(len(result.inserted_ids)) + " new items in " + collection_name)

    def insert_many_into(self, collection_name, data_points):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_many(data_points)

    def insert_one_into(self, collection_name, data_point):
        self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_one(data_point)

    def get_max_timestamp(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find().sort('unixTime', -1).limit(1)

    def get_max_timestamp_nmaprun(self):  # todo test
        # db.nmaprun.find().sort({'nmaprun.@start':-1}).collation({locale: 'en_US', numericOrdering: true}).limit(1)
        return self.mongo[constants.PI_DATABASE_NAME]['nmaprun'].find().sort('nmaprun.@start', -1).collation(
            {'locale': 'en_US', 'numericOrdering': True}).limit(1)

    def select_all(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find()