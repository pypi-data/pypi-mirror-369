import json
from typing import List

from m3cli.models.interactive_parameter import InteractiveParameter
from m3cli.services.request_service import BaseRequest, POST, SdkClient
from m3cli.utils.interactivity_utils import get_interactivity_option

PARAMETERS_HANDLER_ATTRIBUTE = 'parameters_handler'


class ParametersProvider:

    def __init__(self, interactive_options):
        self.interactive_options = interactive_options

    def fetch_interactive_parameters(
            self,
            request_parameters,
    ) -> List[InteractiveParameter]:
        """
        This function gets parameters for command's request
        which will be asked from user in Interactive mode.
        :return: list of parameters
        """
        api_action = get_interactivity_option(
            interactive_options=self.interactive_options,
            option_name=PARAMETERS_HANDLER_ATTRIBUTE,
        )
        get_params_request = BaseRequest(
            command='get_parameters',
            api_action=api_action,
            parameters=request_parameters,
            method=POST,
        )
        request_mapping, response = SdkClient().execute(
            request=get_params_request,
        )
        response = response[0]  # always a single item in a list
        if not response.get('data'):
            error_message = 'An error has occurred while processing the request'
            if response.get('readableError'):
                error_message += response.get('readableError')
            else:
                error_message += response.get('error')
            raise AssertionError(error_message)
        raw_parameters = json.loads(response.get('data'))
        return [InteractiveParameter(each) for each in raw_parameters]
