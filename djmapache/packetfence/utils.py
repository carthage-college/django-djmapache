# -*- coding: utf-8 -*-

import requests
import json

from django.conf import settings

API_EARL = settings.PACKETFENCE_API_EARL


def get_token():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = dict(
        username=settings.PACKETFENCE_USERNAME,
        password=settings.PACKETFENCE_PASSWORD
    )
    url = API_EARL + settings.PACKETFENCE_LOGIN_ENDPOINT
    resp = requests.post(url=url, data=json.dumps(params), headers=headers, verify=False)
    return json.loads(resp.content)['token']
