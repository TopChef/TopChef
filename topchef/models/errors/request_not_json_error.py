from topchef.models import APIError


class RequestNotJSONError(APIError):
    """
    Thrown if a request is provided to this API that isn't JSON
    """
    @property
    def status_code(self) -> int:
        return 400

    @property
    def title(self) -> str:
        """

        :return:
        """
        return "Request Not JSON"

    @property
    def detail(self) -> str:
        """

        :return:
        """
        return "Could not undertand input. Either it is not JSON, or the " \
               "type was not specified using the Content-Type header"
