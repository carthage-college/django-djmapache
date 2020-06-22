# -*- coding: utf-8 -*-

"""API views."""

import json

import requests
import urllib3
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from djimix.decorators.auth import portal_auth_required
from djmapache.indahaus.manager import Client
from djmapache.packetfence.settings.local import API_EARL
from djmapache.packetfence.utils.helpers import get_token as get_token_nac
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@portal_auth_required(
    session_var='DJMAPACHE_INDAHAUS_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def spa(request):
    """Display all clients for all domain controllers for SPA."""
    client = Client()
    domains = settings.INDAHAUS_RF_DOMAINS
    for idx, domain in enumerate(domains):
        token = client.get_token()
        devices = client.get_devices(domain[0], token)
        pids = []
        if devices:
            # auth token from NAC
            headers = {
                'accept': 'application/json', 'Authorization': get_token_nac(),
            }
            for device_wap in devices:
                ap = device_wap['ap']
                mac = device_wap['mac'].replace('-', ':')
                url = '{0}{1}/{2}'.format(
                    API_EARL, settings.PACKETFENCE_NODE_ENDPOINT, mac,
                )
                response = requests.get(url=url, headers=headers, verify=False)
                device_nac = response.json()

                for key, _ in device_nac['item'].items():
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
                            # check for areas within a domain
                            if domains[idx][1]['areas']:
                                for area in domains[idx][1]['areas']:
                                    if ap in area[2]:
                                        if pid not in area[1]:
                                            area[1].append(pid)
            # update RF domain with the total number of pids
            domains[idx][1]['pids'] = len(pids)
            # update areas with total number of pids
            if domains[idx][1]['areas']:
                for aid, _ in enumerate(domains[idx][1]['areas']):
                    length = len(domains[idx][1]['areas'][aid][1])
                    domains[idx][1]['areas'][aid][1] = length

        # sign out
        client.destroy_token(token)
    return HttpResponse(
        json.dumps(domains), content_type='text/plain; charset=utf-8',
    )


@portal_auth_required(
    session_var='DJMAPACHE_INDAHAUS_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def clients(request, domain):
    """Display all clients given a domain controller identifier."""
    client = Client()
    token = client.get_token()
    devices = client.get_devices(domain, token)
    pids = []
    if devices:
        # auth token from NAC
        headers = {
            'accept': 'application/json', 'Authorization': get_token_nac(),
        }
        for device_wap in devices:
            mac = device_wap['mac'].replace('-', ':')
            url = '{0}{1}/{2}'.format(
                API_EARL, settings.PACKETFENCE_NODE_ENDPOINT, mac,
            )
            response = requests.get(url=url, headers=headers, verify=False)
            device_nac = response.json()

            for key, _ in device_nac['item'].items():
                if key == 'pid':
                    pid = device_nac['item'][key].lower()
                    if pid not in pids:
                        pids.append(pid)

    # sign out
    client.destroy_token(token)
    jason = json.dumps({'pids': pids, 'count': len(pids)})
    return HttpResponse(jason, content_type='text/plain; charset=utf-8')
