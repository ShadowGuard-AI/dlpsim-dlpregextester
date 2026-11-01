import argparse
import re
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="DLP Regex Tester: Highlights matches in a text file based on a regex.")
    parser.add_argument("regex", help="The regular expression to test.")
    parser.add_argument("file_path", help="The path to the text file to scan.")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Perform case-insensitive matching.")
    parser.add_argument("-l", "--log-level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Set the logging level.")
    parser.add_argument("--redact", action="store_true", help="Mask the middle of each matched value, keeping only its first and last characters.")
    return parser


def mask_value(value):
    """Masks the middle of a matched value."""
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "*" * (len(value) - 2) + value[-1]


def highlight_matches(text, regex, ignore_case=False, redact=False):
    """
    Highlights all matches of the regex in a single line of text.
    Uses ANSI escape codes to highlight the matches. With redact, the
    middle of each matched value is masked before highlighting.
    Returns a pair: the highlighted line, or None on an invalid
    pattern, and the number of matches found.
    """
    flags = re.IGNORECASE if ignore_case else 0
    try:
        matches = list(re.finditer(regex, text, flags=flags))
    except re.error as e:
        logging.error(f"Invalid regular expression: {e}")
        return None, 0  # Indicate an error

    highlighted_text = ""
    last_end = 0
    for match in matches:
        start, end = match.span()
        # Redaction covers the matches only. The rest of a printed
        # line, including text right beside a masked value, goes to
        # the terminal in clear, so --redact is not a promise that a
        # shown line contains nothing sensitive.
        shown = mask_value(text[start:end]) if redact else text[start:end]
        highlighted_text += text[last_end:start]
        highlighted_text += f"\033[1;31m{shown}\033[0m"  # Red and bold highlight
        last_end = end
    highlighted_text += text[last_end:]
    return highlighted_text, len(matches)


def main():
    """
    Main function to execute the DLP Regex Tester.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(args.log_level)

    # Input Validation: Check if the file exists.
    try:
        with open(args.file_path, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {args.file_path}")
        sys.exit(1)
    except IOError as e:
        logging.error(f"Error reading file: {e}")
        sys.exit(1)

    if not text:
        print("File is empty: no content was scanned.")
        sys.exit(1)

    # Core Functionality: Print only the lines containing matches,
    # with the matches highlighted. Lines without matches are not
    # printed, so values the pattern does not select are not echoed.
    # Matching runs one line at a time, which quietly redefines the
    # pattern: ^ and $ anchor to each line as if MULTILINE were set,
    # and a pattern written to span a line break can never match,
    # because no single call ever sees two lines together.
    total_matches = 0
    for line in text.splitlines():
        highlighted_line, count = highlight_matches(line, args.regex, args.ignore_case, args.redact)
        if highlighted_line is None:
            # An invalid pattern is the one thing this tool exists to test, so
            # it has to read as a failure. It used to print nothing and exit 0.
            sys.exit(1)
        if count:
            total_matches += count
            print(highlighted_line)

    print(f"Summary: {total_matches} matches found, {len(text.encode('utf-8'))} bytes scanned.")


if __name__ == "__main__":
    """
    Entry point of the script.
    """
    main()

# Usage Examples:
# 1. Basic usage: python main.py "\d{3}-\d{2}-\d{4}" test.txt
# 2. Case-insensitive: python main.py "[a-z]+@[a-z]+\.com" test.txt -i
# 3. Change the logging level: python main.py "\d+" test.txt -l DEBUG