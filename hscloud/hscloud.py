from .helpers import Helpers
from hscloud.hscloudexception import HsCloudException, HsCloudAccessDeniedException, HsCloudFlowControlException
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
        try:
            response = Helpers.login(self.username, self.password)
            self.endpoint = response.get("endpoint")
            self.access_token = response.get("access_token")
            return True
        except HsCloudException as e:
            logger.error(e)
            return False
        except HsCloudAccessDeniedException as e:
            logger.error(e)
            return False
        except HsCloudFlowControlException as e:
            logger.error(e)
            return False

    def get_devices(self):
        try:
            return Helpers.devices(self.endpoint, self.access_token)
        except HsCloudException as e:
            logger.error(e)
            return None
        except HsCloudAccessDeniedException as e:
            logger.error(e)
            return None
        except HsCloudFlowControlException as e:
            logger.error(e)
            return None

    def get_status(self, devicesn):
        try:
            return Helpers.status(self.endpoint, self.access_token, devicesn)
        except HsCloudException as e:
            logger.error(e)
            return None
        except HsCloudAccessDeniedException as e:
            logger.error(e)
            return None
        except HsCloudFlowControlException as e:
            logger.error(e)
            return None

    def update_status(self, devicesn, **kwargs):
        return Helpers.update(self.endpoint, self.access_token, devicesn, **kwargs)