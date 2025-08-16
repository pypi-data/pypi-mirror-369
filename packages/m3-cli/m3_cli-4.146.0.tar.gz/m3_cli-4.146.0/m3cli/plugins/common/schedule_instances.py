import json
from os import linesep


def format_response(response, verb, preposition):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    successful = []
    failed = []
    for response_item in response:
        if bool(response_item.get('success')):
            successful.append(response_item)
        else:
            failed.append(response_item)
    if not failed:
        return f'Instances were {verb} {preposition} the schedule.'
    if not successful:
        sample_reason = failed[0].get('reason')
        if all(fail_item.get('reason') == sample_reason for fail_item in failed):
            return f'Instances were not {verb} {preposition} ' \
                   f'the schedule.{linesep}Reason: {sample_reason}'

    result_table = []
    for success_item in successful:
        result_table.append({
            "Instance": success_item.get('instancesId'),
            "Status": verb.capitalize()
        })
    for fail_item in failed:
        result_table.append({
            "Instance": fail_item.get('instancesId'),
            "Status": f'Not {verb}',
            "Reason": fail_item.get('reason')
        })
    return result_table
