"""
Here are static methods to check response content.
Please be aware that beginning from the version [3.45.22] - response data will
be presented as list. You should consider it while working with response to
prevent unexpected issues.
"""


def contains_string_data(response):
    return len(response) == 1 and isinstance(response[0], str)


def contains_dict_data(response):
    return len(response) == 1 and isinstance(response[0], dict)


def contains_empty_data(response):
    # remove this code after __remove_none refactoring
    return response in [[{}], [[]], [None], [''], {}, [], '', None]
