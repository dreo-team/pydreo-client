import requests
from datetime import datetime
from typing import Optional
from hscloud.hscloudexception import HsCloudException, HsCloudBusinessException, HsCloudAccessDeniedException, HsCloudFlowControlException

class Helpers:

    @staticmethod
    def login(username=None, password=None):
        base_url = 'https://open-api-us.dreo-cloud.com'

        headers = {
            'Content-Type': 'application/json',
            'UA': 'openapi/1.0.0'
        }

        params = {
            'timestamp': Helpers.timestamp()
        }

        body = {
            "client_id": "89ef537b2202481aaaf9077068bcb0c9",
            "client_secret": "41b20a1f60e9499e89c8646c31f93ea1",
            "grant_type": "openapi",
            "scope": "all",
            "email": username,
            "password": password
        }

        return Helpers.call_api(base_url + "/api/oauth/login", "post", headers, params, body)

    @staticmethod
    def devices(endpoint=None, access_token=None):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'UA': 'openapi/1.0.0'
        }

        params = {
            'timestamp': Helpers.timestamp()
        }

        return Helpers.call_api(endpoint + "/api/device/list", "get", headers, params)

    @staticmethod
    def status(endpoint=None, access_token=None, devicesn=None):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'UA': 'openapi/1.0.0'
        }

        params = {
            'deviceSn': devicesn,
            'timestamp': Helpers.timestamp()
        }

        return Helpers.call_api(endpoint + "/api/device/state", "get", headers, params)

    @staticmethod
    def update(endpoint=None, access_token=None, devicesn=None,  **kwargs):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'UA': 'openapi/1.0.0'
        }

        params = {
            'timestamp': Helpers.timestamp()
        }

        return Helpers.call_api(endpoint + "/api/device/control", "post", headers, params, Helpers.update_body(devicesn, **kwargs))

    @staticmethod
    def call_api(api: str, method: str, headers: Optional[dict] = None, params: Optional[dict] = None, json_body: Optional[dict] = None) -> tuple:
        result = None
        response = None
        try:
            if method.lower() == "get":
                response = requests.get(api, headers=headers, params=params, timeout=8)

            elif method.lower() == "post":
                response = requests.post(api, headers=headers, params=params, json=json_body, timeout=8)

        except requests.exceptions.RequestException as e:
            raise HsCloudException(e)
        else:
            if response.status_code == 200:
                response_body = response.json()
                code = response_body.get("code")
                if code == 0:
                    result = response_body.get("data")
                elif code == 401:
                    raise HsCloudAccessDeniedException("invalid auth")
                else:
                    raise HsCloudBusinessException(response_body.get("msg"))

            elif response.status_code == 429:
                raise HsCloudFlowControlException("Your request is too frequent, please try again later.")
            else:
                raise HsCloudException("There is a service problem, please try again later.")

        return result

    @staticmethod
    def update_body(devicesn, **kwargs):
        data = {
            'devicesn': devicesn
        }

        desired = {}
        for key, value in kwargs.items():
            desired.update({key: value})

        data.update({'desired': desired})
        return data

    @staticmethod
    def timestamp():
        return int(datetime.now().timestamp() * 1000)