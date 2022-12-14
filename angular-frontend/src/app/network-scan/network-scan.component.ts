import { Component, OnInit } from '@angular/core';
import * as echarts from 'echarts';
import { EChartsCoreOption } from 'echarts';
import { Util } from 'src/app/util';
import GraphHelper from 'src/models/graphHelper';
import { HostInformation } from 'src/models/hostInformation';
import Constants from '../constants';

@Component({
  selector: 'app-network-scan',
  templateUrl: './network-scan.component.html',
  styleUrls: ['./network-scan.component.css']
})
export class NetworkScanComponent implements OnInit {

  nmapCustomCommandSuffix = "-sS -T4 -F --traceroute " + Constants.IP_NETWORK_PREFIX + "*";

  topologyStyles = ['Port Count', 'Network/Subnetwork'];
  selectedStyle: string = this.topologyStyles[0];

  networkgraphDOM!: HTMLElement;
  networkGraph!: echarts.ECharts;
  loadingScan: boolean = false;
  nmapNetworkScan: any;
  subNetwork: any;

  lastUpdatedNmap: string = 'never';
  lastUpdatedSubnetwork: string = 'never';

  isRefreshing: boolean = false
  refreshIntervalId: any

  hostInformation!: HostInformation;

  constructor() { }


  ngOnInit(): void {
    this.networkgraphDOM = document.getElementById("networkgraph")! as HTMLElement
    this.networkGraph = echarts.init(this.networkgraphDOM)

    // init graph plotter
    let options: EChartsCoreOption = {
      title: {
        text: "Topology"
      },
      tooltip: {},
      animationEasingUpdate: "linear",
      draggable: true,

      series: [
        {
          type: "graph",
          chartDataZoom: true,
          layout: "force",
          symbolSize: 20,
          roam: true, // mouse moving

          label: {
            position: "bottom"
          },
          draggable: false,
          force: {
            repulsion: 1500,
            gravity: 0.2,
            friction: 0.6,
            layoutAnimation: false
          },
          animation: false,

          edgeSymbol: ["none", "none"],
          edgeSymbolSize: [4, 10],
          edgeLabel: {
            fontSize: 20
          },
          lineStyle: {
            opacity: 1,
            curveness: 0
          }
        }
      ]
    };

    this.networkGraph.on('click', (params) => this.onClickGraph(params))

    this.networkGraph.setOption(options)

    this.getLastNetworkReport()
  }

  // Execute a nmap scan command
  async onClickExecuteCustomNetworkScan() {
    let nmapCustomNetworkScan = await this.fetchNetworkScan('GET', 'custom_network_scan/' + this.nmapCustomCommandSuffix) as any
    this.nmapNetworkScan = nmapCustomNetworkScan.response.nmaprun
    this.subNetwork = null

    let util = new Util()
    this.lastUpdatedNmap = util.convertUnixTimeToDate(nmapCustomNetworkScan.response.nmap_unixTime)
    this.lastUpdatedSubnetwork = 'never'

    this.setNetworkReport()
  }

  // Show host information if a node in the network graph plotter is clicked
  private onClickGraph(params: any) {
    if (params.dataType == 'node') {
      console.log((params.name));

      for (const host of this.nmapNetworkScan.host) {
        let hostIp = ""
        if (Array.isArray(host.address)) {
          hostIp = host.address[0]["@addr"]
        } else {
          hostIp = host.address["@addr"]
        }

        let hostNameIp = hostIp + (host.hostnames?.hostname["@name"] ? '\n(' + host.hostnames?.hostname["@name"] + ')' : '')
        if (hostNameIp == params.name) {
          this.hostInformation = new HostInformation(host)
        }
      }
    }
  }

  // Get the last network report from the backend/database
  async getLastNetworkReport() {
    let lastReport = await this.fetchNetworkScan('GET', 'last_network_scan') as any
    this.nmapNetworkScan = lastReport.response.nmaprun
    this.subNetwork = lastReport.response.subnetwork

    let util = new Util()
    this.lastUpdatedNmap = util.convertUnixTimeToDate(lastReport.response.nmap_unixTime)
    this.lastUpdatedSubnetwork = util.convertUnixTimeToDate(lastReport.response.subnetwork_unixTime)

    this.setNetworkReport()
  }

  // perform a full network scan including the zigbee subnetworks
  async onClickGetFullNetworkReport() {
    let networkScan = await this.fetchNetworkScan('GET', 'full_network_scan/' + this.nmapCustomCommandSuffix) as any

    this.nmapNetworkScan = networkScan.response.nmaprun
    this.subNetwork = networkScan.response.subnetwork

    let util = new Util()
    this.lastUpdatedNmap = util.convertUnixTimeToDate(networkScan.response.nmap_unixTime)
    this.lastUpdatedSubnetwork = util.convertUnixTimeToDate(networkScan.response.subnetwork_unixTime)

    this.setNetworkReport()
  }

  // Fetch a network scan from the backend
  private async fetchNetworkScan(method: string, route: string) {
    let networkScanReport
    try {
      let util = new Util
      this.loadingScan = true
      networkScanReport = await util.fetchFromBackend(method, route) as any
    } catch (error: any) {
      alert(error.message)
      return
    } finally {
      this.loadingScan = false
    }

    return networkScanReport
  }

  // Set the network report to the model of this view
  private setNetworkReport() {
    // check if hosts found
    if (this.nmapNetworkScan?.host == null) {
      console.log("No hosts found!");

      return
    }

    this.hostInformation = new HostInformation(this.nmapNetworkScan.host[0])

    // set graph
    let graphHelper: GraphHelper = new GraphHelper()
    let graphContent = graphHelper.getGraphContent(this.nmapNetworkScan, this.subNetwork, this.selectedStyle)

    this.networkGraph.setOption({
      series: {
        data: graphContent.nodeList,
        links: graphContent.linkList
      }
    })
  }

  onChangeNodeColorStyle(event: any) {
    this.setNetworkReport()
  }
}
