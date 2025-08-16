import argparse
from datetime import datetime
import os
from pathlib import Path
from m3cli.docs.commons import create_logger
from m3cli.docs.commons.commands_table import add_table_md
from m3cli.docs.cli_to_md import generate_documentation
from m3cli.docs.commons.m3_preprocessor import style_headers, merge_mds
from m3cli.docs.md_to_docx import convert_md_to_docx
from m3cli.docs.commons.title_page_docx import add_page_to_docx

_LOG = create_logger()


def generate_docx(
        tool_name: str,
        commands_def_path: str,
        result_docx_path: str | None = None,
) -> None:
    tmp_md_path = os.path.join(result_docx_path, f'{tool_name}.md')
    _LOG.debug(f"Temporary markdown path set: {tmp_md_path}")
    generate_documentation(
        tool_name,
        commands_def_path,
        result_docx_path,
    )
    result_docx_path = \
        os.path.join(result_docx_path, f'{tool_name}_reference_guide.docx')
    _LOG.debug(f"Result DOCX path set: {result_docx_path}")

    style_headers(tmp_md_path, tmp_md_path)
    if not add_table_md(tmp_md_path, tmp_md_path):
        _LOG.warning("Failed to parse the MD file or no commands found.")

    merge_mds(
        [os.path.join(Path(__file__).parent, "commons/m3_intro.md"), tmp_md_path],
        tmp_md_path,
        delimiter='\n \n\n',
    )

    current_date = datetime.now()
    current_month_year = current_date.strftime('%B %Y')

    convert_md_to_docx(tmp_md_path, result_docx_path)
    add_page_to_docx(
        result_docx_path,
        '>Maestro CLI\nReference Guide',
        'M3RG-01',
        current_month_year,
        'Version 1',
    )


parser = argparse.ArgumentParser()
parser.add_argument(
    '-name', '--tool_name', type=str, required=True,
    help='The name of the tool for which the doc will be generated'
)
parser.add_argument(
    '-cmd_path', '--commands_def_path', type=str, required=True,
    help='The path to the file "commands_def.json"'
)
parser.add_argument(
    '-res_path', '--result_docx_path', type=str,
    help='The path to the result file DOCX file'
)


def main():
    try:
        generate_docx(**vars(parser.parse_args()))
    except Exception as e:
        _LOG.exception(e)


if __name__ == '__main__':
    main()
