from .helpers import Helpers
from hscloud.hscloudexception import HsCloudException, HsCloudBusinessException, HsCloudAccessDeniedException, HsCloudFlowControlException
import logging

logger = logging.getLogger(__name__)

class HsCloud:

    def __init__(self, username=None, password=None):
        super().__init__()
        self.username = username
        self.password = password
        self.endpoint = None
        self.access_token = None

    def login(self):
        response = Helpers.login(self.username, self.password)
        self.endpoint = response.get("endpoint")
        self.access_token = response.get("access_token")
        return response

    def get_devices(self):
        return Helpers.devices(self.endpoint, self.access_token)

    def get_status(self, devicesn):
        return Helpers.status(self.endpoint, self.access_token, devicesn)

    def update_status(self, devicesn, **kwargs):
        return Helpers.update(self.endpoint, self.access_token, devicesn, **kwargs)