import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.SubnetworkHandler import SubnetworkHandler


# static method which starts an endless zigbee2mqtt service with a given delay time
def start_zigbee2mqtt_network_state_service(delay: int):
    while True:
        execute_zigbee2mqtt_scan()

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def execute_zigbee2mqtt_scan():
    print("Get zigbee2mqtt network state " + " (" + current_process().name + ")")

    # get from database (no new nmap scan)
    database_handler = DatabaseHandler(constants.MONGO_URI)
    nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    nmap_handler = NmapHandler()
    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    subnetwork_handler = SubnetworkHandler()
    subnetwork_handler.scan_subnetwork(ssh_hosts)
