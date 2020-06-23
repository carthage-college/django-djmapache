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
    # obtain all devices connected to an RF Domain
    domains = settings.INDAHAUS_RF_DOMAINS
    for idx, domain in enumerate(domains):
        token = client.get_token()
        devices = client.get_devices(domain['name'], token)
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
                    print('ap = {0}'.format(ap))
                    print('mac = {0}'.format(mac))
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
                        # some folks are registered with both their username
                        # and their email address for some reason.
                        if '@{0}'.format(settings.LDAP_EMAIL_DOMAIN) in pid:
                            pid = pid.split('@')[0]
                        status = (
                            pid not in settings.INDAHAUS_XCLUDE and
                            'host/' not in pid and
                            'carthage\\' not in pid
                        )
                        if status:
                            if pid not in pids:
                                pids.append(pid)
                                if settings.DEBUG:
                                    print(
                                        'domain AP = {0}/{1}'.format(ap, pid),
                                    )
                            # check for areas within a domain
                            if domains[idx]['areas']:
                                for area in domains[idx]['areas']:
                                    if ap in area['aps']:
                                        if settings.DEBUG:
                                            print('area AP = {0} / {1}'.format(
                                                ap, pid,
                                            ))
                                        if pid not in area['pids']:
                                            area['pids'].append(pid)

            # update RF domain with the total number of pids
            domains[idx]['pids'] = len(pids)
            print('++++++++++++++++++++++++++++')
            print(
                {
                    'domain': domains[idx]['name'],
                    'pids': domains[idx]['pids'],
                    'count': len(domains[idx]['pids']),
                },
            )
            # update areas with total number of pids
            if domains[idx]['areas']:
                print('areas:')
                for aid, _ in enumerate(domains[idx]['areas']):
                    length = len(domains[idx]['areas'][aid]['pids'])
                    domains[idx]['areas'][aid]['pids'] = length
                    print(domains[idx]['areas']['name'])
                    print(domains[idx]['areas'][aid]['pids'])
            print('----------------------------')
        client.destroy_token(token)


if __name__ == "__main__":

    sys.exit(main())
