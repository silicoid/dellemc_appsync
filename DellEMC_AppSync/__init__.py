import requests
import urllib.parse
import re


class DellEMC_AppSync:
    """Dell EMC AppSync manages array based copies. This module
    is a wrapper to the Dell EMC AppSync REST API"""

    def __init__(self, username=None, password=None, host=None, port=None,
                 ssl=True, verify=True, verbose=0):
        """Username, password and host are the minimum requirements to Connect
        to AppSync. If ssl is set to anything else but 'y' then http is used.
        Default is y."""

        if verbose >= 3:
            print("Parameters:", username, password, host, port, ssl)

        if port is None:
            if ssl is True:
                self.port = "8445"
            else:
                self.port = "8085"
        if ssl is True:
            self.protocol = "https"
        else:
            self.protocol = "http"

        self.verify = verify

        if (username is not None and
                password is not None and
                host is not None):
            self.username = username
            self.password = password
            self.host = host
        else:
            print("Oh god, oh god. We'll all gonna die.")

        if verify is False:
            requests.packages.urllib3.disable_warnings()

        # Create session
        self.session = requests.Session()

        # Request to get CAS URL
        url = self.protocol + "://" + self.host + ":" + self.port + \
            "/appsync/rest/types/license/instances"

        if verbose >= 1:
            print("Requesting: " + url)

        response = self.session.get(url, verify=self.verify)
        for resp in response.history:
            self.cas_url = (re.search("http[s]*://.*:[0-9]*/.*/",
                                      resp.headers["Location"]))[0]

        self.jsessionid = re.search(";jsessionid=([0-9A-F]+)",
                                    response.text, re.IGNORECASE).group(1)

        self.lt = re.search("name=\"lt\" value=\"(.*)\"",
                            response.text, re.IGNORECASE).group(1)

        if verbose >= 3:
            print("jsessionid:", self.jsessionid)
            print("LT:", self.lt)

        # Login
        url = self.cas_url + ";jsessionid=" + self.jsessionid + \
            "?submit=Login&username=" + self.username + \
            "&password=" + urllib.parse.quote(self.password) + \
            "&lt=" + self.lt + \
            "&execution=e1s1&_eventId=submit"
        if verbose >= 3:
            print("CAS:", url)

        response = self.session.get(url, verify=self.verify)

        if response.status_code != 200:
            raise Exception("Login not succesful")
        if re.search("value=\"Login\"", response.text,
                     re.IGNORECASE) is not None:
            raise Exception("Login not successful")


def __del__(self):
    url = self.cas_url + "logout"
    self.session.get(url, verify=self.verify)
