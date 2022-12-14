import { Component, OnInit } from '@angular/core';
import Constants from '../constants';
import { Util } from '../util';

@Component({
  selector: 'app-home',
  templateUrl: './services.component.html',
  styleUrls: ['./services.component.css']
})
export class ServicesComponent implements OnInit {

  availableServices: any = []
  selectedStartService: string = ''
  serviceStartRequestParameter: string = '?delay=60'

  runningServices: any = []

  isRefreshing: boolean = false
  loadingRefresh: boolean = false

  refreshIntervalId: any

  constructor() { }

  ngOnInit(): void {
    this.getRunningServices()
    this.startRefreshInterval()
    this.getAvailableServices()
  }

  // Start the autmatic refresh interval.
  private startRefreshInterval() {
    this.isRefreshing = true
    console.log('auto-refresh started');

    this.refreshIntervalId = setInterval(() => {
      this.getRunningServices()
    }, 3000);
  }

  // Get current running services in the backend 
  async getRunningServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'running_services') as any

    this.runningServices = response.response
  }

  // Get a list of the available services
  async getAvailableServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'available_services') as any

    this.availableServices = response.response
  }

  // Stop a given service
  async stopService(element: any) {
    let util = new Util
    // stop with pid
    let response = await util.fetchFromBackend('GET', 'stop/' + element.pid) as any
    console.log(response.response);

    this.getRunningServices()
  }

  // Toggle the auto refresh
  onChangeAutoRefresh(event: any) {
    if (this.isRefreshing) {
      this.startRefreshInterval()
    } else {
      console.log('auto-refresh stopped');

      clearInterval(this.refreshIntervalId)
    }
  }

  // Start a given service
  async onClickStartService(event: any) {
    if (this.selectedStartService) {
      let util = new Util
      try {
        let response = await util.fetchFromBackend('GET', 'start/' + this.selectedStartService + this.serviceStartRequestParameter) as any
        alert(response.response)
      } catch (error) {
        alert(error)
      }
    } else {
      alert('Select service first!')
    }
  }
}
