import os
import re
from m3cli.docs.commons import create_logger

_LOG = create_logger()


def style_headers(old_md_file, new_md_file):
    try:
        with open(old_md_file, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        _LOG.error(f"File not found: {old_md_file}")
        raise
    except Exception as e:
        _LOG.error(f"Error reading file {old_md_file}: {e}")
        raise

    # Replace `*m3 text*` with `# m3 text`
    text = re.sub(
        r'^\*(m3.+)\*$',  # pattern
        r'# \1',  # replacement
        text,
        flags=re.MULTILINE,
    )
    # Replace `Text:` with `### Text:`
    text = re.sub(
        r'^(Description:|Examples?:|Related commands:).*$',
        r'### \1',
        text,
        flags=re.MULTILINE,
    )
    # Replace `Text: text` with `**Text:** text`
    text = re.sub(
        r'^(Parameters:|Usage:)(.*)$',
        r'**\1**\2',
        text,
        flags=re.MULTILINE,
    )
    # Add {{ pagebreak }}
    text = re.sub(
        r'\n# m3',  # pattern
        r'\n{{ pagebreak }}\n\n# m3',  # replacement
        text,
        flags=re.MULTILINE,
    )
    try:
        with open(new_md_file, 'w') as file:
            file.write(text)
        _LOG.info(f"Styled Markdown file saved to: {new_md_file}")
    except Exception as e:
        _LOG.error(f"Error writing to file: {new_md_file}: {e}")
        raise


def merge_mds(md_files, output_file, delimiter="\n"):
    content = []
    for md_file in md_files:
        full_path = os.path.abspath(md_file)

        if not os.path.exists(full_path):
            _LOG.error(f"The file: {full_path} does not exist.")
            continue

        try:
            with open(full_path, "r") as file:
                file_content = file.read()
                content.append(file_content)
        except Exception as e:
            _LOG.error(f"Error reading file {full_path}: {e}")
            continue

    merged_content = delimiter.join(content)
    try:
        with open(output_file, "w") as file:
            file.write(merged_content)
        _LOG.info(f"Markdown files merged successfully into: {output_file}")
    except Exception as e:
        _LOG.error(f"Error writing merged content to: {output_file}: {e}")
        raise
