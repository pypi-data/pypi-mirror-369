#!/user/bin/env -S uv run --script
# /// script
# dependencies = ["typer","rich"]
# ///
"""
MarkDown File Manipulation (MNM) - Tools for converting various file formats to Markdown.

This module provides functionality to convert different file types to Markdown format
for inclusion in documentation, reports, or Markdown-based websites. It supports a variety
of formats including CSV, JSON, code files with syntax highlighting, and plain text.

The intended interface is the command-line through Typer and more specifically to
be used with `uv run`. The main features include:

1. Automatic file format detection based on file extension
2. Conversion of CSV files to Markdown tables with customizable formatting
3. Pretty-printing and syntax highlighting for JSON and code files
4. Direct inclusion of existing Markdown files
5. Addition of file timestamps and other metadata
6. A file-reference system that can update Markdown files by replacing special comment tags

Key components:
- ToMarkdown: Abstract base class for all converters
- Various format-specific converter classes (CsvToMarkdown, JsonToMarkdown, etc.)
- markdown_factory: Factory function to create the appropriate converter
- Command-line interface for converting files or updating Markdown files with file references

NOTE: This module is SUPPOSED to be a single file so it is easy to use as a tool with uv.

Usage example:
    # Via CLI
    # python mnm.py report.md --bold "Important,Critical"
"""
import csv
import json
import pathlib
import re
import shlex
import subprocess
from abc import ABC, abstractmethod
from io import StringIO
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

class ToMarkdown(ABC):
    """Abstract base class for converting files to Markdown format.

    This class provides functionality to load file content and convert it to
    markdown representation. Concrete subclasses must implement the `to_markdown()`
    method to define specific conversion logic.

    Attributes:
        file_name: Path to the file to be converted.
        text: Content of the loaded file.
        markdown: The markdown representation after conversion.
        error_str: Error message if file loading fails.
    """

    def __init__(self, file_name: str, **kwargs):
        self.file_name: str = file_name
        self.text: str = self.load_file()
        self.markdown: str = ""
        self.error_str: str = ""
        # Store remaining kwargs if needed
        self.kwargs = kwargs

    def load_file(self, file_name: str | None = None) -> str:
        """Load the content of a file into the text attribute.

        Reads the file specified by file_name (or the instance's file_name if not provided)
        and stores its content in the text attribute. If any file-related error occurs,
        the error message is stored in the error_str attribute and text is set to an empty string.

        Args:
            file_name: Path to the file to load. If None, uses self.file_name.

        Returns:
            The content of the file as a string, or an empty string if an error occurred.

        Side effects:
            - Sets self.text to the file content
            - Sets self.error_str to an error message if any exception occurs

        Exceptions handled:
            - FileNotFoundError: When the file doesn't exist
            - FileExistsError: When there's an issue with file existence
            - IOError: For general I/O errors
            - PermissionError: When access to the file is denied
        """
        file_name = file_name or self.file_name
        try:
            with open(file_name, 'r', encoding='utf8') as file:
                self.text = file.read()
        except (FileNotFoundError, FileExistsError, IOError, PermissionError) as e:
            self.error_str = str(e)
            self.text = ''

        return self.text

    @abstractmethod
    def to_markdown(self):
        """Subclasses must override this method."""

    def to_full_markdown(self):
        """Generate full markdown including any headers and footers that might be configured.

        The method calls to_markdown() and adds timestamp footer if date_stamp is True.

        Returns:
            The complete markdown representation.
        """

        md = self.to_markdown()

        return md


class MarkdownToMarkdown(ToMarkdown):
    """Directly inserts the contents of a Markdown file into the output."""

    def to_markdown(self):
        return f"\n{self.text}\n"


class TextToMarkdown(ToMarkdown):
    """Converts plain text files to Markdown code blocks."""

    def __init__(self, file_name: str, **kwargs):
        super().__init__(file_name, **kwargs)

    def to_markdown(self):
        """Returns the text content wrapped in a plain Markdown code block."""
        return f"```\n{self.text}\n```"


class JsonToMarkdown(ToMarkdown):
    """Converts JSON files to formatted Markdown code blocks with syntax highlighting."""

    def to_markdown(self):
        """Returns the JSON content as a formatted, indented block with json syntax."""
        formatted_json = json.dumps(json.loads(self.text), indent=4)
        return f"```json\n{formatted_json}\n```"


class CsvToMarkdown(ToMarkdown):
    """Converts JSON files to formatted Markdown code blocks with syntax highlighting."""

    def __init__(self, file_name: str, **kwargs):
        # Extract CSV-specific parameters before calling super()
        self.auto_break = kwargs.pop('auto_break', True)
        self.bold_vals = kwargs.pop('bold_vals', [])

        # Pass remaining kwargs to super
        super().__init__(file_name, **kwargs)

    def to_markdown(self):
        try:
            with open(self.file_name, 'r', encoding='utf8') as csv_file:
                reader = csv.reader(csv_file)

                # Read all rows from the CSV
                rows = list(reader)

                if not rows:
                    return "The CSV file is empty."

                # Prepare the Markdown table header
                header = rows[0]

                # Insert line breaks
                if self.auto_break:
                    header = [h.replace(" ", "<br>").replace("_", "<br>") for h in header]

                markdown = "| " + " | ".join(header) + " |\n"
                markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

                # Add the rows
                for row in rows[1:]:
                    formatted_row = []
                    for item in row:
                        try:
                            if item in self.bold_vals:
                                item = f"-> **{item}** <-"
                            # Check if the item is numeric (can be converted to a float)
                            number = float(item)
                            # Format as a 2-significant-figure float (if it's not an integer)
                            if number.is_integer() and '.' not in str(number):
                                formatted_row.append(f"{int(number)}")  # Keeps integers as they are
                            else:
                                formatted_row.append(f"{number:.02f}")
                        except ValueError:
                            # If not numeric, keep the item as-is
                            formatted_row.append(item)

                    markdown += "| " + " | ".join(formatted_row) + " |\n"

                return markdown
        except FileNotFoundError:
            return f"Error: File '{self.file_name}' not found."
        except Exception as e:
            return f"Error: An error occurred while processing the file: {e}"


class CodeToMarkdown(ToMarkdown):
    """Converts code formatted Markdown based on the fil extension of the file."""

    def __init__(self, file_name: str, language: str, **kwargs):
        super().__init__(file_name, **kwargs)
        self.language = language

    def to_markdown(self):
        return f"```{self.language}\n{self.text}\n```"


def markdown_factory(filename: str, **kwargs):
    """
    Creates the appropriate markdown converter based on file extension.

    This factory function examines the provided file's extension and instantiates
    the corresponding converter class. All keyword arguments are passed through to
    the converter's constructor, allowing each converter to use parameters relevant
    to its functionality.

    Args:
        filename (str): Path to the file that needs conversion to markdown.
        **kwargs: Additional keyword arguments that will be passed to the converter.
            CSV-specific parameters:
                auto_break (bool): Whether to insert line breaks in CSV headers.
                bold_vals (list): List of values to be bolded in CSV tables.

    Returns:
        ToMarkdown: An instance of the appropriate converter subclass:
            - MarkdownToMarkdown: For .md files
            - CodeToMarkdown: For code files (.py, .java, .js, etc.)
            - CsvToMarkdown: For .csv files
            - JsonToMarkdown: For .json files
            - TextToMarkdown: For unrecognized file types

    """
    # Convert filename to Path object and get the extension
    path = pathlib.Path(filename)
    ext = path.suffix.lower()

    # Map of file extensions to language identifiers for code blocks
    # Some languages have multiple possible extensions
    language_map = {
        # Python
        '.py': 'python',
        '.pyw': 'python',
        '.pyx': 'python',
        '.pyi': 'python',

        # JavaScript
        '.js': 'javascript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',

        # TypeScript
        '.ts': 'typescript',
        '.tsx': 'typescript',

        # INI
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.properties': 'ini',

        # Java
        '.java': 'java',

        # C/C++
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.hxx': 'cpp',

        # C#
        '.cs': 'csharp',

        # PHP
        '.php': 'php',
        '.phtml': 'php',
        '.php5': 'php',

        # Ruby
        '.rb': 'ruby',
        '.rake': 'ruby',

        # Go
        '.go': 'go',

        # Rust
        '.rs': 'rust',
        '.rlib': 'rust',

        # Swift
        '.swift': 'swift',

        # Kotlin
        '.kt': 'kotlin',
        '.kts': 'kotlin',

        # SQL
        '.sql': 'sql',

        # Web technologies
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'scss',
        '.less': 'less',

        # Shell/Bash
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.fish': 'bash',

        # YAML
        '.yaml': 'yaml',
        '.yml': 'yaml',

        # XML
        '.xml': 'xml',
        '.xsd': 'xml',
        '.xsl': 'xml',

        # Markdown
        '.md': 'markdown',
        '.markdown': 'markdown',

        # JSON
        '.json': 'json',
        '.jsonc': 'json',

        # VB.NET
        '.vb': 'vbnet',

        # Other common languages
        '.r': 'r',
        '.pl': 'perl',
        '.pm': 'perl',
        '.lua': 'lua',
        '.elm': 'elm',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.scala': 'scala',
        '.clj': 'clojure',
        '.erl': 'erlang',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.dart': 'dart',
        '.groovy': 'groovy',
        '.jl': 'julia',
        '.m': 'matlab',
        '.ps1': 'powershell',
        '.tf': 'terraform',
        '.dockerfile': 'dockerfile',
    }

    # Special case handlers
    special_handlers = {
        '.md': MarkdownToMarkdown,
        '.markdown': MarkdownToMarkdown,
        '.csv': CsvToMarkdown,
        '.json': JsonToMarkdown,
    }

    # Check for special handlers first
    if ext in special_handlers:
        return special_handlers[ext](filename, **kwargs)

    # For code files with recognized extensions
    if ext in language_map:
        return CodeToMarkdown(filename, language_map[ext], **kwargs)

    # Default case for unrecognized file types
    return TextToMarkdown(filename, **kwargs)


def update_file_inserts(content: str, bold: str, auto_break: bool) -> str:
    """
    Replace file insertion placeholders with file contents converted to markdown.

    Args:
        content (str): The Markdown content as a string.
        bold (str): Comma-separated values to bold.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: Updated content with file placeholders replaced.
    """
    # Regex to find <!--file ...--> blocks
    file_pattern = r'<!--file\s+(.+?)-->(.*?)<!--file end-->'
    file_matches = re.finditer(file_pattern, content, re.DOTALL)
    file_matches = list(file_matches)

    new_content = content

    # Process file insertions
    for match in file_matches:
        # Extract options for processing
        kwargs = {
            'bold_vals': bold.split(",") if bold else [],
            'auto_break': auto_break,
        }

        glob_pattern = match.group(1).strip()  # Extract the glob pattern
        old_block = match.group(0)  # Original block

        # Get all matching files using pathlib
        matching_files = list(pathlib.Path().glob(glob_pattern))

        # Generate markdown for each matching file
        if matching_files:
            markdown_parts = []
            for file_path in matching_files:
                file_name = str(file_path)
                md_gen = markdown_factory(file_name, **kwargs)
                markdown_text = md_gen.to_full_markdown()
                markdown_parts.append(markdown_text)

            # Join all markdown parts with a separator
            all_markdown = "\n\n".join(markdown_parts)
            new_block = f"<!--file {glob_pattern}-->\n{all_markdown}\n<!--file end-->"
        else:
            # No files found - add a comment indicating that
            new_block = f"<!--file {glob_pattern}-->\n<!-- No files found matching pattern '{glob_pattern}' -->\n<!--file end-->"

        new_content = new_content.replace(old_block, new_block,1)

    return new_content


def update_process_inserts(content: str, timeout_sec=30) -> str:
    """
    Replace process execution placeholders with command output using Rich for formatting.

    Args:
        content (str): The Markdown content as a string.
        timeout_sec (int): Timeout in seconds for each process execution. Default is 30 seconds.

    Returns:
        str: Updated content with process placeholders replaced with command output.
    """

    # Process pattern handling
    proc_pattern = r'^<!--process\s+(.+?)-->(.*?)<!--process end-->'
    proc_matches = re.finditer(proc_pattern, content, re.DOTALL)
    proc_matches = list(proc_matches)

    new_content = content

    # Process command executions
    for match in proc_matches:
        command = match.group(1).strip()  # Extract the command
        old_block = match.group(0)  # Original block

        # Create a string buffer to capture Rich output
        string_io = StringIO()
        console = Console(file=string_io, width=100, highlight=False)

        try:
            # Execute the command and capture output
            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                shell=False,
                text=True,
                check=True,
                timeout=timeout_sec
            )

            # Format the output using Rich
            console.print(result.stdout.strip())
            output = string_io.getvalue()

            # Create new block with command output
            new_block = f"<!--process {command}-->\n```text\n{output}\n```\n<!--process end-->"


        except subprocess.TimeoutExpired:
            console.print(Panel.fit(
                f"Command execution timed out after {timeout_sec} seconds",
                title="Timeout Error",
                style="bold red"
            ))
            output = string_io.getvalue()
            new_block = f"<!--process {command}-->\n{output}\n<!--process end-->"

        new_content = new_content.replace(old_block, new_block,1)

    return new_content


def update_markdown_from_string(content: str, bold: str, auto_break: bool) -> str:
    """
    Parse a Markdown string and replace special placeholders with actual file contents
    or process output.

    Supported placeholders:
        1. <!--file <glob_pattern>--> : Replaces with the Markdown tables based on file extension
           for all files matching the glob pattern
        2. <!--process <command>--> : Executes the command and inserts its stdout output

    Args:
        content (str): The Markdown content as a string.
        bold (str): Whether to apply bold styling for certain values.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: The updated Markdown content with placeholders replaced.
    """
    try:
        # Apply file insertions
        content = update_file_inserts(content, bold, auto_break)

        # Apply process insertions
        content = update_process_inserts(content)

        return content

    except Exception as e:
        typer.echo(f"An error occurred while updating the Markdown: {e}", err=True)
        return content  # Return original content in the case of error


def update_markdown_file(
        md_file: str,
        bold: str = '',
        auto_break: bool = False,
        out_file: str | None = None,
) -> str:
    """
    Updates a Markdown (.md) file with specified modifications (handled by
    update_markdown_from_string). The file update can be overridden by providing an out_file
    parameter. The normal use case is to update a Markdown file in place.

    Args:
        md_file (str): Path to the Markdown file to be read.
        bold (str, optional): String to be added in bold text format. Defaults to an empty string.
        auto_break (bool): If True, applies automatic line breaking within the content.
        out_file (str, optional): If provided, writes the updated Markdown content to this file.
            Otherwise, updates the original file.

    Returns:
        str: Updated content of the Markdown file after modifications.

    Raises:
        FileNotFoundError: If the specified `md_file` is not found.
        Exception: If an unexpected error occurs during the update process.
    """
    try:
        # Read file content
        with open(md_file, 'r', encoding='utf8') as file:
            content = file.read()

        # Call the string-based update function
        updated_content = update_markdown_from_string(content, bold, auto_break)

        # Write updated content to the specified output file
        out_file = out_file or md_file
        with open(out_file, 'w', encoding='utf8') as file_out:
            file_out.write(updated_content)

        return updated_content

    except FileNotFoundError as fnf_error:
        raise FileNotFoundError(f"File '{md_file}' not found.") from fnf_error



def handle_update_markdown_file(
        md_file: str,
        bold: str = '',
        auto_break: bool = False,
        out_file: str | None = None,
) -> str:
    """
    Wrapper for `update_markdown_file` that integrates with Typer for CLI interaction.

    Args:
        md_file (str): Path to the Markdown file to be read.
        bold (str, optional): String to be added in bold text format. Defaults to an empty string.
        auto_break (bool): If True, applies automatic line breaking within the content.
        out_file (str, optional): File to save the updated content. Defaults to overwriting
            the input file.

    Returns:
        None
    """
    try:
        updated_content = update_markdown_file(md_file,
                                               bold,
                                               auto_break,
                                               out_file
                                               )

        typer.echo(f"File '{md_file}' updated successfully.", err=True)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)

    return updated_content


app = typer.Typer(add_completion=False,rich_markup_mode=None)



@app.command()
def convert(
        file_name: str = typer.Argument("README.md", help="The file to convert to Markdown"),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file (if not specified, prints to stdout)"
        ),
        bold_values: Optional[str] = typer.Option(
            None, "--bold", "-b", help="Comma-separated values to make bold (for CSV files)"
        ),
        auto_break: Optional[bool] = typer.Option(
            True, "--auto-break/--no-auto-break", help="Disable automatic line breaks in CSV headers"
        ),
        plain: bool = typer.Option(
            False, "--plain", help="Output plain markdown without rich formatting"
        ),

):
    """Convert a file to Markdown based on its extension."""
    try:

        markdown_text = handle_update_markdown_file(file_name,
                                                    bold=bold_values,
                                                    auto_break=auto_break)

        if output:
            with open(output, "w", encoding='utf8') as file:
                file.write(markdown_text)
            typer.echo(f"Markdown written to {output}", err=True)
        else:
            if markdown_text:
                if not plain:
                    # Use Rich to display formatted markdown
                    console = Console()
                    md = Markdown(markdown_text)
                    console.print(md)
                else:
                    # Output plain markdown
                    typer.echo(markdown_text)

            else:
                typer.echo("An Error Occurred", err=True)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
