from topchef.models.interfaces import APIException


class NotUUIDError(APIException):
    def __init__(self, not_a_uuid: str) -> None:
        """

        :param not_a_uuid: The string that could not be converted to a UUID
        """
        self.bad_string = not_a_uuid

    @property
    def title(self) -> str:
        return "Not UUID Error"

    @property
    def detail(self) -> str:
        return 'The string %s could not be converted to a UUID' % (
            self.bad_string
        )

    @property
    def status_code(self) -> int:
        return 404
