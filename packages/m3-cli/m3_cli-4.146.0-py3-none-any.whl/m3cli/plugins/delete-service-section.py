"""
The custom logic for the command m3 delete-service-section.
This logic is processing the input some parameters.
"""
from operator import xor, and_
from functools import reduce


def create_custom_request(request):
    params = request.parameters
    blocks_without_title = bool(params.get('deleteBlockWithoutTitle'))
    all_blocks = bool(params.get('deleteAllBlocks'))
    block_title = params.get('blockTitle')
    bool_list = (blocks_without_title, all_blocks, bool(block_title))
    if not reduce(xor, bool_list) or reduce(and_, bool_list):
        raise AssertionError(
            "Specify only one of the following parameters: '--block-title', "
            "'--delete-all', '--delete-empty' ")

    params.update({'deleteBlockWithoutTitle': blocks_without_title,
                   'deleteAllBlocks': all_blocks,
                   'blockTitle': block_title if block_title else ""
                   })

    return request
