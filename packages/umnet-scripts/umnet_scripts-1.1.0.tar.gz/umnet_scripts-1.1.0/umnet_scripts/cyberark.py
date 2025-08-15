#!/usr/bin/env python3

from os import path
import sys
import requests
import urllib3
from decouple import Config, RepositoryEnv


class Cyberark(object):
    def __init__(self, environment):
        if path.exists("cyberark.env"):
            self.env_file = "cyberark.env"
        elif path.exists("/usr/local/umnet/lib/cyberark/cyberark.env"):
            self.env_file = "/usr/local/umnet/lib/cyberark/cyberark.env"
        else:
            raise LookupError("Environment file, cyberark.env, can't be found")

        self.env_config = Config(RepositoryEnv(self.env_file))

        self.url_base = self.env_config.get("URL_BASE")
        self.url_aim_endpoint = self.env_config.get("URL_AIM_ENDPOINT")
        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }

        if environment.upper() == "UMNET":
            self.cert = (self.env_config.get("CERT"), self.env_config.get("KEY"))
            self.appid = self.env_config.get("APPID")
            self.safe = self.env_config.get("SAFE")
        elif environment.upper() == "NSO":
            self.cert = (self.env_config.get("NSO_CERT"), self.env_config.get("NSO_KEY"))
            self.appid = self.env_config.get("NSO_APPID")
            self.safe = self.env_config.get("NSO_SAFE")
        elif environment.upper() == "DEARBORN":
            self.cert = (self.env_config.get("DEARBORN_CERT"), self.env_config.get("DEARBORN_KEY"))
            self.appid = self.env_config.get("DEARBORN_APPID")
            self.safe = self.env_config.get("DEARBORN_SAFE")

    def query_cyberark(self, password_entity):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if sys.version.startswith('3.8'):
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

        i = 0
        retry_counter = 0

        while i == 0:
            try:
                aim_url = self.url_base + self.url_aim_endpoint + self.appid + self.safe + "&Object=" + password_entity
                acct = requests.get(aim_url, headers=self.headers, cert=self.cert, verify=True)

                passwd = acct.json()["Content"]
                i = 1
                return passwd

            except Exception as e:
                retry_counter = retry_counter + 1
                if retry_counter == 10:
                    raise e
