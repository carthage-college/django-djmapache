#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

import requests
import urllib3
from django.conf import settings
from djmapache.packetfence.settings.local import API_EARL
from djmapache.packetfence.utils.helpers import get_token as get_nac_token
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_token():
    """Obtain the authorization token from the API."""
    response = requests.get(
        '{0}/{1}'.format(settings.WING_API_EARL, settings.WING_ENDPOINT_LOGIN),
        auth=(settings.WING_USERNAME, settings.WING_PASSWORD),
        verify=False,
    )
    jason = response.json()
    return jason['data']['auth_token']


def api_logout(token):
    """Sign out from the API."""
    # curl
    # -X GET
    # --cookie auth_token=xxxxxxxxx
    # -k https://0.0.0.0/rest/v1/act/logout
    return True


def main():
    """Display the number of nodes."""
    for domain in settings.WING_RF_DOMAINS:
        token_wing = get_token()
        url = '{0}/{1}/{2}/{3}'.format(
            settings.WING_API_EARL,
            settings.WING_ENDPOINT_STATS,
            settings.WING_ENDPOINT_STATS_WIRELESS,
            settings.WING_ENDPOINT_STATS_WIRELESS_CLIENTS,
        )
        if settings.DEBUG:
            print(url)

        controller = {'rf-domain': domain}
        if settings.DEBUG:
            print('++++++++++++++++++++++++++++')
            print('domain controller: {0}'.format(controller))
            print('++++++++++++++++++++++++++++')
        response = requests.post(
            url,
            cookies={'auth_token': token_wing},
            data=json.dumps(controller),
            verify=False,
        )
        jason = response.json()
        # auth token from NAC
        token_nac = get_nac_token()
        if settings.DEBUG:
            print(token_nac)
        headers = {
            'accept': 'application/json', 'Authorization': token_nac,
        }
        if settings.DEBUG:
            print(headers)

        pids = []
        for device_wifi in jason['data']:
            mac = device_wifi['mac'].replace('-', ':')
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
                # print(key, device_nac['item'][key])
                if key == 'pid' and device_nac['item'][key] not in pids:
                    pids.append(device_nac['item'][key])
            print('++++++++++++++++++++++++++++')
        print(pids)
        print('count: {0}'.format(len(pids)))


if __name__ == "__main__":

    sys.exit(main())
