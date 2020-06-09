#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import requests
import urllib3
from django.conf import settings
from djmapache.indahaus.manager import Client
from djmapache.packetfence.settings.local import API_EARL
from djmapache.packetfence.utils.helpers import get_token as get_token_nac
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    """Display the number of nodes."""
    client = Client()
    for domain in settings.INDAHAUS_RF_DOMAINS:
        token = client.get_token()
        devices = client.get_devices(domain, token)
        if devices:
            pids = []
            # auth token from NAC
            headers = {
                'accept': 'application/json', 'Authorization': get_token_nac(),
            }
            if settings.DEBUG:
                print(headers)
            for device_wap in devices:
                mac = device_wap['mac'].replace('-', ':')
                if settings.DEBUG:
                    print(mac)
                url = '{0}{1}/{2}'.format(
                    API_EARL, settings.PACKETFENCE_NODE_ENDPOINT, mac,
                )
                if settings.DEBUG:
                    print(url)
                response = requests.get(url=url, headers=headers, verify=False)
                device_nac = response.json()
                for key, _ in device_nac['item'].items():
                    if settings.DEBUG:
                        print(key, device_nac['item'][key])
                    if key == 'pid':
                        pid = device_nac['item'][key].lower()
                        if pid not in pids:
                            pids.append(pid)
                if settings.DEBUG:
                    print('++++++++++++++++++++++++++++')
            print('++++++++++++++++++++++++++++')
            print('domain controller: {0}'.format(domain))
            print('++++++++++++++++++++++++++++')
            print('count: {0}'.format(len(pids)))
            print('folks:')
            print(pids)
            client.destroy_token(token)


if __name__ == "__main__":

    sys.exit(main())
