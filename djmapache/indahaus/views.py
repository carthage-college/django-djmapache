# -*- coding: utf-8 -*-

"""API views."""

import requests
import urllib3
from django.conf import settings
from django.shortcuts import render
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
def clients(request):
    """Display all clients for all domain controllers."""
    client = Client()
    domains = []
    for domain in settings.INDAHAUS_RF_DOMAINS:
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
        domains.append({'domain': domain, 'pids': pids, 'count': len(pids)})
    return render(request, 'indahaus/clients.html', {'domains': domains})


@portal_auth_required(
    session_var='DJMAPACHE_INDAHAUS_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def spa(request):
    return render(request, 'indahaus/spa.html', {})
