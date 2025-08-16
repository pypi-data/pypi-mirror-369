import re
from m3cli.docs.commons import create_logger

_LOG = create_logger()


def parse_md_file(input_file):
    try:
        with open(input_file, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        _LOG.exception(f"File not found: {input_file}")
        raise
    except Exception as e:
        _LOG.error(f"Error reading file: {input_file}: {e}")
        raise

    # Split the content into sections based on headers
    sections = re.split(r'\n#[^#]', content)
    commands = []

    for section in sections:
        if section.startswith("#"):
            # Remove the leading '#' from the section title
            section = section[1:]

        command_match = re.search(r"\*\*Usage:\*\*\s+(.+)", section)
        description_match = re.search(r"### Description:\s*\n\n(.+)", section)

        if command_match and description_match:
            command = command_match\
                .group(1).strip().replace("[parameters]", "").strip()
            description = description_match.group(1).strip()
            # Extract the first line of the section to use as a header link
            header_match = section.split("\n", 1)[0].strip()
            header = header_match.replace(' ', '-').lower() \
                if header_match else command.lower().replace(' ', '-')
            commands.append((command, description, header))

    _LOG.info(f"Extracted {len(commands)} commands from the file.")
    return commands, content


def create_md_table(output_file, commands, content):
    try:
        with open(output_file, 'w') as file:
            file.write("| Command | Description |\n")
            file.write("| --- | --- |\n")
            for command, description, header in commands:
                file.write(f"| [{command}](#{header}) | {description} |\n")
            file.write("\n{{ pagebreak }}\n\n" + content)
    except Exception as e:
        _LOG.error(f"Error writing to file {output_file}: {e}")
        raise


def add_table_md(input_file, output_file):
    try:
        commands, content = parse_md_file(input_file)
        if commands:
            create_md_table(output_file, commands, content)
            return True
        else:
            _LOG.warning("No commands found to add to the table.")
            return False
    except Exception as e:
        _LOG.error(f"Failed to add table to markdown: {e}")
        return False
