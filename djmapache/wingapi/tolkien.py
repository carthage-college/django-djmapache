#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import requests
from django.conf import settings


def main():
    """Display the number of nodes."""
    url = '{0}/{1}'.format(settings.WING_API_EARL, settings.WING_ENDPOINT_LOGIN)
    resp = requests.get(
        url,
        auth=(settings.WING_USERNAME, settings.WING_PASSWORD),
        verify=False,
    )
    jason = resp.json()
    return jason['data']['auth_token']


if __name__ == "__main__":

    sys.exit(main())
