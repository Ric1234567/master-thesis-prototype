import array
import string

from flask_pymongo import MongoClient

import constants
from handler.ssh.SshInformation import SshInformation


def filter_data_points_for_collection(collection_name: string, data_points: array):
    result = []
    for data_point in data_points:
        if data_point['name'] == collection_name:
            result.append(data_point)
    return result


# class which is responsible for database operations
class DatabaseHandler:

    def __init__(self, mongo_uri):
        self.mongo = MongoClient(mongo_uri)  # here mongo_client; but parameter is string to mongodb server

    # convert data string into python dict list
    @staticmethod
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

    # write multiple data string to the database and add a host_ip to every data point
    def insert_many_to_database_with_host_ip(self, collection_name: string, data: string, ssh_information: SshInformation):
        data_points = self.preprocess_data_string(data)
        data_points = filter_data_points_for_collection(collection_name, data_points)

        # add ip
        for data_point in data_points:
            data_point['host_ip'] = ssh_information.ip

        if len(data_points) > 0:
            result = self.insert_many_into(collection_name, data_points)
            print(str(len(result.inserted_ids)) + " new items in " + collection_name)

    # insert many data points to a specific collection
    def insert_many_into(self, collection_name, data_points):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_many(data_points)

    # insert a single data point to a specific collection
    def insert_one_into(self, collection_name, data_point):
        self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_one(data_point)

    # select a data point of a specific collection which has the highest unix timestamp (= the newest data point)
    def select_max_timestamp(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find().sort('unixTime', -1).limit(1)

    # convert cursor to single entry
    def select_latest_entry(self, collection_name):
        cursor = self.select_max_timestamp(collection_name)
        for entry in cursor:
            return entry

    # get the latest zigbee2mqtt entry of a specific host
    def select_latest_zigbee2mqtt_entry_of_host(self, host_ip):
        cursor = self.mongo[constants.PI_DATABASE_NAME][constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE]\
            .find({'host': host_ip}).sort('unixTime', -1).limit(1)
        for entry in cursor:
            return entry

    # get the latest mosquitto entry of a specific host
    def select_latest_mosquitto_entry_of_host(self, host_ip):
        cursor = self.mongo[constants.PI_DATABASE_NAME][constants.COLLECTION_NAME_MOSQUITTO_CONFIG]\
            .find({'host': host_ip}).sort('unixTime', -1).limit(1)
        for entry in cursor:
            return entry

    # get all entries of a specific collection
    def select_all(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find()
