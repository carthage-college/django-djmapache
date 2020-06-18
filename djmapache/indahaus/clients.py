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

XCLUDE = ['default', 'admin', '1']


def main():
    """Display the number of nodes."""
    client = Client()
    # obtain all devices connected to an RF Domain
    for domain in settings.INDAHAUS_RF_DOMAINS:
        token = client.get_token()
        devices = client.get_devices(domain[0], token)
        # if we have some devices go to the NAC to find out who
        # they are based on MAC
        pids = []
        if devices:
            # auth token from NAC
            headers = {
                'accept': 'application/json', 'Authorization': get_token_nac(),
            }
            if settings.DEBUG:
                print(headers)
            # iterate over the devices from the NAC to remove any duplicate
            # users who might have more than one device registered in an
            # RF Domain.
            for device_wap in devices:
                ap = device_wap['ap']
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
                        email = (
                            '@' in pid and
                            pid.split('@')[1] != settings.LDAP_EMAIL_DOMAIN
                        )
                        status = (
                            pid not in pids and
                            pid not in XCLUDE and
                            'host/' not in pid and
                            'carthage\\' not in pid
                        )
                        if status:
                            pids.append(pid)
            area = {
                'domain': domain[0],
                'pids': pids,
                'count': len(pids),
            }
            print('++++++++++++++++++++++++++++')
            print(area)
            print('++++++++++++++++++++++++++++')
        client.destroy_token(token)


if __name__ == "__main__":

    sys.exit(main())
