from typing import List

from m3cli.models.interactive_parameter import InteractiveParameter
from m3cli.services.interactivity.constants import STRING_TYPE


def get_interactivity_option(interactive_options, option_name, required=True):
    attribute = interactive_options.get(option_name)
    if attribute is None and required:
        raise AssertionError(f'{option_name} in not specified')
    return attribute


def unavailable_values_detector(parameters: List[InteractiveParameter]):
    return (param for param in parameters
            if param.value is None
            and (param.type != STRING_TYPE or param.value_provided_by_user))
