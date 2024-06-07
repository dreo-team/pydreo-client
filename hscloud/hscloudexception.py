
class HsCloudException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class HsCloudBusinessException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class HsCloudAccessDeniedException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class HsCloudFlowControlException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)