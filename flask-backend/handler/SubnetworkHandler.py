import time
from multiprocessing import current_process

from handler.ssh.SshInformation import SshInformation
from util import ConfigurationHelper
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler


# class which handles (zigbee/mqtt) subnetwork data
class SubnetworkHandler:
    # scan all ssh hosts for subnetworks
    def scan_subnetwork(self, ssh_hosts):
        all_subnetworks = []
        for ssh_host in ssh_hosts:
            subnetwork = self.scan_subnetwork_host(ssh_host)
            all_subnetworks.append(subnetwork)

        subnetwork_scan = {
            'unixTime': round(time.time()),
            'scans': all_subnetworks
        }

        # write subnetwork information to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of subnetwork scan to database (" + current_process().name + ")")
        database_handler.insert_one_into(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE,
                                         subnetwork_scan)

    # scan a given ssh host for subnetworks.
    # It reads the information from the zigbee2mqtt configuration and its state.json
    def scan_subnetwork_host(self, ssh_information: SshInformation):
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port, constants.SSH_USER,
                                 constants.SSH_PASSWORD)
        ssh_handler.connect()

        # download zigbee2mqtt state.json (holds information of connected devices via zigbee)
        ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME,
                                           constants.ZIGBEE2MQTT_REMOTE_FILE_PATH)

        # download zigbee2mqtt configuration.yaml file which holds naming information of connected devices
        ssh_handler.download_file_via_sftp(
            constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG,
            constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)

        ssh_handler.disconnect()

        # read state.json file from output file dir
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME, 'r') as file:
            data_point_string = file.read()
        data_point = eval(data_point_string)

        # read configuration.yaml file from output file dir
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG, 'r') as file:
            config_string = file.read()

        config = ConfigurationHelper.parse_yaml_configuration_string(config_string)

        # build subnetwork object
        subnetwork = {
            'host': ssh_information.ip,
            'state': data_point,
            'config': config
        }
        return subnetwork

    # gets the latest subnetwork information from database
    def get_latest_subnetwork_information(self):
        # get latest entry
        database_handler = DatabaseHandler(constants.MONGO_URI)
        latest_entry = database_handler.get_latest_entry(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE)
        subnetwork = []

        # build subnetwork object with timestamp
        if 'scans' in latest_entry:
            for scan in latest_entry['scans']:
                connected_subnetwork_hex = list(scan['state'])
                config_file = scan['config']

                for connected_device_hex in connected_subnetwork_hex:
                    tmp_dict = {
                        'hex': connected_device_hex,
                        'host': scan['host'],
                        'name': config_file['devices'][connected_device_hex]['friendly_name']
                    }
                    subnetwork.append(tmp_dict)

        return subnetwork, latest_entry['unixTime']
