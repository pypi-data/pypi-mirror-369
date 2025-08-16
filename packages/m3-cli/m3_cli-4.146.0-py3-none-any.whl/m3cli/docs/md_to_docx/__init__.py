import pypandoc
from m3cli.docs.md_to_docx.custom_styles import apply_custom_styles
from m3cli.docs.commons import create_logger

_LOG = create_logger()


def convert_md_to_docx(md_file, docx_file):
    try:
        # Convert a Markdown file to a DOCX file using Pandoc
        pypandoc.convert_file(md_file, 'docx', outputfile=docx_file)
        _LOG.info(f"Successfully converted: {md_file} to: {docx_file}")
    except Exception as e:
        _LOG.error(f"Failed to convert {md_file} to DOCX: {e}")
        raise

    try:
        # Apply custom styles to the newly created DOCX file
        apply_custom_styles(docx_file)
        _LOG.info(f"Custom styles applied successfully to: {docx_file}")
    except Exception as e:
        _LOG.error(f"Failed to apply custom styles to: {docx_file}: {e}")
        raise
