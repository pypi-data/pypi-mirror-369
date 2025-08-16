import re
import argparse
import json
import os
import subprocess
from m3cli.docs.commons import create_logger
from progressbar import Percentage, ETA, ProgressBar

_LOG = create_logger()


def cut_string(s: str, pattern: str) -> tuple[str, str]:
    match = re.search(pattern, s, re.MULTILINE)
    if match:
        return s[:match.start()] + s[match.end():], match.group()
    else:
        return s, ""


def generate_documentation(
        tool_name: str,
        commands_def_path: str,
        result_md_path: str | None = None,
) -> None:
    result_md_path = result_md_path or '.'
    helps_array = []
    if not os.path.isfile(commands_def_path):
        _LOG.error(
            f'Specified path to the commands file "{commands_def_path}" '
            f'is not valid!'
        )
        return
    with open(commands_def_path, 'r+') as f:
        command_def = json.load(f).get('commands')

    PROGRESS_WIDGET = ['Gathering helps | ', Percentage(), ' | ', ETA()]
    pbar = ProgressBar(widgets=PROGRESS_WIDGET, maxval=len(command_def.keys()))
    pbar.start()
    progress_bar_iterator = 0
    # ========================= Logic part =====================================
    for cmd_name in command_def.keys():
        help_string = f'{tool_name} {cmd_name}'
        raw_help = subprocess.check_output(
            help_string + ' --full-help',
            stderr=subprocess.STDOUT,
            shell=True,
        ).decode('utf-8')
        if raw_help.startswith('You are using an outdated version of m3-cli'):
            raw_help = '\n'.join(raw_help.split('\n')[3:])
        # Remove redundant new lines
        raw_help = '\n\n'.join(line for line in raw_help.split('\n') if line.strip())
        raw_help = raw_help.replace("\r", "")

        raw_help, usage = cut_string(
            raw_help + "\n", r"Usage: .+\n\nParameters:\n(?:\s+\S.+\n)+",
        )
        list_help = raw_help.split("\n")
        index = next((
            index for index, value in enumerate(list_help)
            if value.startswith("Example:") or value.startswith("Examples:")
        ))
        list_help.insert(index, usage)
        raw_help = "\n".join(list_help)

        helps_array.append('*' + help_string + '*' + os.linesep + raw_help)
        # ===================== Logic part =====================================
        progress_bar_iterator += 1
        pbar.update(progress_bar_iterator)
    pbar.finish()

    result_md_path = os.path.join(result_md_path, f'{tool_name}.md')
    with open(result_md_path, 'w+') as f:
        f.write(os.linesep.join(helps_array))
    _LOG.info(
        f'Result doc file has been successfully created by path: {result_md_path}'
    )


parser = argparse.ArgumentParser()
parser.add_argument(
    '-name', '--tool_name', type=str, required=True,
    help='The name of the tool for which the doc will be genarated'
)
parser.add_argument(
    '-cmd_path', '--commands_def_path', type=str, required=True,
    help='The path to the file "commands_def.json"'
)
parser.add_argument(
    '-res_path', '--result_md_path', type=str,
    help='The path to the result file MD file'
)


def main():
    try:
        generate_documentation(**vars(parser.parse_args()))
    except Exception as e:
        _LOG.exception(e)


if __name__ == "__main__":
    main()
