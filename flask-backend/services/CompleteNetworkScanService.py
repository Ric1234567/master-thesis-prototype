import string
import time
from multiprocessing import current_process, Process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.ssh.SshInformation import SshInformation
from services import MosquittoScanService, OsqueryScanService, NmapScanService, Zigbee2MqttScanService
from services.Service import Service


# Service which runs in an endless manner.
# Performs a complete execution of all other service scans (except analysisScanService).
class CompleteNetworkScanService(Service):
    def __init__(self, name: string, description: string, args: tuple):
        process = Process(name=name,
                          target=self.start_complete_network_scan_service,
                          args=args)
        super().__init__(name, description, args, process)

    # static method which starts an endless complete network scan with a given nmap command and its execution delay
    def start_complete_network_scan_service(self, nmap_command: string, delay: int):
        while True:
            execute_complete_network_scan(nmap_command)

            # sleep for the delay time
            print(current_process().name + " sleeping for " + str(delay) + " seconds!")
            time.sleep(delay)


def execute_complete_network_scan(nmap_command: string):
    # execute nmap scan which gets written to the database
    NmapScanService.execute_nmap_scan(nmap_command)

    # get network scan from database
    database_handler = DatabaseHandler(constants.MONGO_URI)
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    # find ssh hosts
    nmap_handler = NmapHandler()
    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    # execute other service operations
    for ssh_information in ssh_hosts:
        execute_all_service_scans(ssh_information)


def execute_all_service_scans(ssh_information: SshInformation):
    MosquittoScanService.execute_mosquitto_scan(ssh_information)
    OsqueryScanService.execute_osquery_scan(ssh_information)
    Zigbee2MqttScanService.execute_zigbee2mqtt_scan(ssh_information)
