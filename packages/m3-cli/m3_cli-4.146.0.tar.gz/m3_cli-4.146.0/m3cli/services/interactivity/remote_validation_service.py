import json
from typing import List, Mapping

from m3cli.models.interactive_parameter import (
    InteractiveParameter, NAME_ATTR
)
from m3cli.services.request_service import BaseRequest, POST, SdkClient
from m3cli.utils.interactivity_utils import get_interactivity_option

VALIDATION_HANDLER_ATTRIBUTE = 'validation_handler'
ERROR_MESSAGE_ATTR = 'errorMessage'


class RemoteValidationService:

    def __init__(self, interactive_options):
        self.interactive_options = interactive_options

    def validate_parameters(
            self,
            parameters: List[InteractiveParameter],
            service_name: str,
    ) -> Mapping[InteractiveParameter, str]:
        """
        Validates parameters entered by a user.
        :return: A list of invalid items.
        """
        api_action = get_interactivity_option(
            interactive_options=self.interactive_options,
            option_name=VALIDATION_HANDLER_ATTRIBUTE,
        )
        old_payload = [
            param.to_raw_parameter() for param in parameters
        ]
        payload = {
            'dtoList': old_payload,
            'serviceName': service_name,
        }
        validation_result = self._request_remote_validation(
            api_action=api_action, parameters=payload,
        )
        invalid_items = [
            validation_item for validation_item in validation_result
            if validation_item.get(ERROR_MESSAGE_ATTR)
        ]
        invalid_parameters = {}
        for item in invalid_items:
            parameter = next(
                param for param in parameters if param.name == item[NAME_ATTR]
            )
            invalid_parameters[parameter] = item[ERROR_MESSAGE_ATTR]
        return invalid_parameters

    @staticmethod
    def _request_remote_validation(api_action, parameters):
        validate_params_request = BaseRequest(
            command='validate_parameters',
            api_action=api_action,
            parameters=parameters,
            method=POST,
        )
        request_mapping, responses = SdkClient().execute(
            request=validate_params_request)
        response_item = responses[0]
        if not response_item.get('data'):
            raise AssertionError(
                f'Failed to validate parameters while applying '
                f'interactive mode. Reason: {response_item}. '
                f'Please contact Maestro Support Team.')
        return json.loads(response_item.get('data'))
