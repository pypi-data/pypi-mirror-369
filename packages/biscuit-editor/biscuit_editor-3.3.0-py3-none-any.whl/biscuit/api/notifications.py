from .endpoint import Endpoint


class Notifications(Endpoint):
    """Notifications endpoint

    This class is used to interact with the notifications API.
    """

    def __init__(self, *a) -> None:
        super().__init__(*a)
        self.notifications = self.base.notifications

        self.info = self.show = self.notifications.info
        self.warn = self.warning = self.notifications.warning
        self.error = self.notifications.error
        self.notify = self.notifications.notify
