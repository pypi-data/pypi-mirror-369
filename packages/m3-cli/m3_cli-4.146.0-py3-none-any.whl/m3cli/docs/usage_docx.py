import argparse
import os
from datetime import datetime
from pathlib import Path

from m3cli.docs.commons import create_logger
from m3cli.docs.md_to_docx import convert_md_to_docx
from m3cli.docs.commons.title_page_docx import add_page_to_docx

_LOG = create_logger()


def generate_docx(
        tool_name: str,
        result_docx_path: str | None = None,
) -> None:
    md_path = os.path.join(Path(__file__).parent, "commons/m3_setup_guide.md")
    result_docx_path = os.path.join(
        result_docx_path, f'{tool_name}_usage_guide.docx',
    )
    _LOG.debug(f"Result DOCX path set: {result_docx_path}")

    current_date = datetime.now()
    current_month_year = current_date.strftime('%B %Y')

    try:
        convert_md_to_docx(md_path, result_docx_path)
        _LOG.info(
            f"Markdown converted to DOCX successfully at: {result_docx_path}")
    except Exception as e:
        _LOG.error(f"Failed to convert markdown to DOCX: {e}")
        raise

    try:
        add_page_to_docx(
            result_docx_path,
            '>Maestro CLI\nUser Guide',
            'M3UG-01',
            current_month_year,
            'Version 1',
        )
    except Exception as e:
        _LOG.error(f"Failed to add title page to DOCX: {e}")
        raise


parser = argparse.ArgumentParser()
parser.add_argument(
    '-name', '--tool_name', type=str, required=True,
    help='The name of the tool for which the doc will be generated'
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
